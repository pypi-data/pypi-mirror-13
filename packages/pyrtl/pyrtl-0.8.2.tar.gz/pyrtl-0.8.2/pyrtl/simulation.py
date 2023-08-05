"""Classes for executing and tracing circuit simulations."""

from __future__ import print_function, unicode_literals

import sys
import re
import numbers

from .pyrtlexceptions import PyrtlError, PyrtlInternalError
from .core import working_block, PostSynthBlock
from .wire import Input, Register, Const
from .memory import RomBlock, _MemReadBase

# ----------------------------------------------------------------
#    __                         ___    __
#   /__` |  |\/| |  | |     /\   |  | /  \ |\ |
#   .__/ |  |  | \__/ |___ /~~\  |  | \__/ | \|
#


class Simulation(object):
    """A class for simulating blocks of logic step by step."""

    simple_func = {  # OPS
        'w': lambda x: x,
        '~': lambda x: ~x,
        '&': lambda l, r: l & r,
        '|': lambda l, r: l | r,
        '^': lambda l, r: l ^ r,
        'n': lambda l, r: ~(l & r),
        '+': lambda l, r: l + r,
        '-': lambda l, r: l - r,
        '*': lambda l, r: l * r,
        '<': lambda l, r: int(l < r),
        '>': lambda l, r: int(l > r),
        '=': lambda l, r: int(l == r)
    }

    def __init__(
            self, tracer=None, register_value_map=None, memory_value_map=None,
            default_value=0, use_postsynth_map_if_available=True, block=None):
        """ Creates a new circuit simulator

        :param tracer: an instance of SimulationTrace used to store execution results.
        :param use_postsynth_map_if_available: will map the I/O to the block from the
        pre-synthesis block so the names and outputs can be used or generated respectively.
        :param register_value_map: is a map of {Register: value}.
        :param memory_value_map: is a map of maps {Memory: {address: Value}}.
        :param default_value: is the value that all unspecified registers and memories will
         default to. If no default_value is specified, it will use the value stored in the
         object (default to 0)
        :param block: the hardware block to be traced (which might be of type PostSynthesisBlock).
        """

        """ Creates object and initializes it with self._initialize.
        register_value_map, memory_value_map, and default_value are passed on to _initialize.
        """

        block = working_block(block)
        block.sanity_check()  # check that this is a good hw block

        self.value = {}   # map from signal->value
        self.memvalue = {}  # map from (memid,address)->value
        self.block = block
        self.default_value = default_value
        self.tracer = tracer
        self._initialize(register_value_map, memory_value_map)
        self.use_postsynth_map = use_postsynth_map_if_available

    def _initialize(self, register_value_map=None, memory_value_map=None, default_value=None):
        """ Sets the wire, register, and memory values to default or as specified.

        :param register_value_map: is a map of {Register: value}.
        :param memory_value_map: is a map of maps {Memory: {address: Value}}.
        :param default_value: is the value that all unspecified registers and memories will
         default to. If no default_value is specified, it will use the value stored in the
         object (default to 0)
        """

        self.value = {}
        if default_value is None:
            default_value = self.default_value

        # set registers to their values
        reg_set = self.block.wirevector_subset(Register)
        if register_value_map is not None:
            for r in reg_set:
                if r in register_value_map:
                    self.value[r] = register_value_map[r]
                else:
                    self.value[r] = default_value

        # set constants to their set values
        for w in self.block.wirevector_subset(Const):
            self.value[w] = w.val
            assert isinstance(w.val, numbers.Integral)  # for now

        # set memories to their passed values
        if memory_value_map is not None:
            for (mem, mem_map) in memory_value_map.items():
                if isinstance(self.block, PostSynthBlock):
                    mem = self.block.mem_map[mem]  # pylint: disable=maybe-no-member
                for (addr, val) in mem_map.items():
                    if addr < 0 or addr >= 2**mem.addrwidth:
                        raise PyrtlError('error, address outside of bounds')
                    self.memvalue[(mem.id, addr)] = val
                    # TODO: warn if value larger than fits in bitwidth

        defined_roms = []
        # set ROMs to their default values
        for romNet in self.block.logic_subset('m'):
            rom = romNet.op_param[1]
            if isinstance(rom, RomBlock) and rom not in defined_roms:
                for address in range(0, 2**rom.addrwidth):
                    self.memvalue[(rom.id, address)] = rom._get_read_data(address)

        # set all other variables to default value
        for w in self.block.wirevector_set:
            if w not in self.value:
                self.value[w] = default_value

        self.ordered_nets = tuple((i for i in self.block))
        self.edge_update_nets = tuple((self.block.logic_subset('r@')))

    def step(self, provided_inputs):
        """ Take the simulation forward one cycle

        :param provided_inputs: a dictionary mapping wirevectors to their values for this step
        """

        # To avoid weird loops, we need a copy of the old values which
        # we can then use to make our updates from
        prior_value = self.value.copy()

        # Check that all Input have a corresponding provided_input
        input_set = self.block.wirevector_subset(Input)
        supplied_inputs = set()
        for i in provided_inputs:
            sim_wire = i
            if isinstance(self.block, PostSynthBlock) and self.use_postsynth_map:
                sim_wire = self.block.io_map[sim_wire]  # pylint: disable=maybe-no-member
            if sim_wire not in input_set:
                raise PyrtlError(
                    'step provided a value for input for "%s" which is '
                    'not a known input ' % i.name)
            if not isinstance(provided_inputs[i], numbers.Integral) or provided_inputs[i] < 0:
                raise PyrtlError(
                    'step provided an input "%s" which is not a valid '
                    'positive integer' % provided_inputs[i])
            if len(bin(provided_inputs[i]))-2 > sim_wire.bitwidth:
                raise PyrtlError(
                    'the bitwidth for "%s" is %d, but the provided input '
                    '%d requires %d bits to represent'
                    % (sim_wire.name, sim_wire.bitwidth,
                       provided_inputs[i], len(bin(provided_inputs[i]))-2))

            self.value[sim_wire] = provided_inputs[i]
            supplied_inputs.add(sim_wire)

        # Check that only inputs are specified, and set the values
        if input_set != supplied_inputs:
            for i in input_set.difference(supplied_inputs):
                raise PyrtlError(
                    'Input "%s" has no input value specified' % i.name)

        # Do all of the clock-edge triggered operations based off of the priors
        for net in self.edge_update_nets:
            self._edge_update(net, prior_value)

        for net in self.ordered_nets:
            self._execute(net)

        # at the end of the step, record the values to the trace
        # print self.value # Helpful Debug Print
        if self.tracer is not None:
            self.tracer.add_step(self.value)

    def inspect(self, thing):
        """ Get the value of 'thing' in the current simulation cycle. """
        return self.value[thing]

    def _sanitize(self, val, wirevector):
        """Return a modified version of val that would fit in wirevector.

        This function should be applied to every primitive call, and it's
        default behavior is to mask the upper bits of value and return that
        new value.
        """
        return val & wirevector.bitmask

    def _execute(self, net):
        """Handle the combinational logic update rules for the given net.

        This function, along with edge_update, defined the semantics
        of the primitive ops.  Function updates self.value accordingly.
        """
        if net.op in self.simple_func:
            argvals = [self.value[arg] for arg in net.args]
            result = self.simple_func[net.op](*argvals)
            self.value[net.dests[0]] = self._sanitize(result, net.dests[0])
        elif net.op == 'x':
            select, a, b = (self.value[net.args[i]] for i in range(3))
            if select == 0:
                result = a
            else:
                result = b
            self.value[net.dests[0]] = self._sanitize(result, net.dests[0])
        elif net.op == 'c':
            result = 0
            for arg in net.args:
                result = result << len(arg)
                result = result | self.value[arg]
            self.value[net.dests[0]] = self._sanitize(result, net.dests[0])
        elif net.op == 's':
            result = 0
            source = self.value[net.args[0]]
            for b in net.op_param[::-1]:
                result = (result << 1) | (0x1 & (source >> b))
            self.value[net.dests[0]] = self._sanitize(result, net.dests[0])
        elif net.op == 'm':
            # memories act async for reads
            memid = net.op_param[0]
            read_addr = self.value[net.args[0]]
            index = (memid, read_addr)
            mem_lookup_result = self.memvalue.get(index, self.default_value)
            self.value[net.dests[0]] = mem_lookup_result
        elif net.op == 'r' or net.op == '@':
            pass  # registers and memory write ports have no logic function
        else:
            raise PyrtlInternalError('error, unknown op type')

    def _edge_update(self, net, prior_value):
        """Handle the posedge event for the simulation of the given net.

        Combinational logic should have no posedge behavior, but registers and
        memory should.  This function, along with _execute, defined the
        semantics of the primitive ops.  Function updates self.value and
        self.memvalue accordingly (using prior_value)
        """
        if net.op in 'w~&|^n+-*<>=xcsm':
            return  # stateless elements and memory-read
        else:
            if net.op == 'r':
                # copy result from input to output of register
                argval = prior_value[net.args[0]]
                self.value[net.dests[0]] = self._sanitize(argval, net.dests[0])
            elif net.op == '@':
                memid = net.op_param[0]
                write_addr = prior_value[net.args[0]]
                write_val = prior_value[net.args[1]]
                write_enable = prior_value[net.args[2]]
                if write_enable:
                    self.memvalue[(memid, write_addr)] = write_val
            else:
                raise PyrtlInternalError

    def _print_values(self):
        print(' '.join([str(v) for _, v in sorted(self.value.items())]))


# ----------------------------------------------------------------
#    ___       __  ___     __
#   |__   /\  /__`  |     /__` |  |\/|
#   |    /~~\ .__/  |     .__/ |  |  |
#

class FastSimulation(object):
    """A class for running JIT implementations of blocks.

    As of right now (7/12/2015), the interface is the same as Simulation.
    They should still be similar in the future
    """

    def __init__(
            self, register_value_map=None, memory_value_map=None,
            default_value=0, tracer=None, block=None):

        block = working_block(block)
        block.sanity_check()  # check that this is a good hw block

        self.block = block
        self.default_value = default_value
        self.tracer = tracer
        self.context = {}
        self._initialize(register_value_map, memory_value_map)

    def _initialize(self, register_value_map=None, memory_value_map=None, default_value=None):

        if default_value is None:
            default_value = self.default_value

        # set registers to their values
        reg_set = self.block.wirevector_subset(Register)
        if register_value_map is not None:
            for r in reg_set:
                if r in register_value_map:
                    self.context[self.varname(r)] = register_value_map[r]
                else:
                    self.context[self.varname(r)] = default_value

        # set constants to their set values
        for w in self.block.wirevector_subset(Const):
            self.context[self.varname(w)] = w.val

        # set memories to their passed values or default value
        self.context['fastsim_mem'] = {}
        if memory_value_map is not None:
            for (mem, mem_map) in memory_value_map.items():
                for addr, value in mem_map.items():
                    self.context['fastsim_mem'][(mem.id, addr)] = value

        for net in self.block.logic_subset('m'):
            mem = net.op_param[1]
            if isinstance(mem, RomBlock):
                if self.varname(mem) not in self.context:
                    self.context[self.varname(mem)] = mem

        # set all other variables to default value
        for w in self.block.wirevector_set:
            if self.varname(w) not in self.context:
                self.context[self.varname(w)] = default_value

        s = self.compiled()
        self.logic_function = compile(s, '<string>', 'exec')

    def step(self, provided_inputs):
        # update state
        # Note: Performance could be improved by walking backwards through block
        # in topo order, rather than making a full copy of the state every time
        self.prior_context = self.context.copy()
        for net in self.block.logic:  # unordered walk
            if net.op == 'r':
                dest = net.dests[0]
                arg = net.args[0]
                priorval = self.prior_context[self.varname(arg)]
                self.context[self.varname(dest)] = dest.bitmask & priorval
            elif net.op == '@':
                memid = net.op_param[0]
                write_addr = self.prior_context[self.varname(net.args[0])]
                write_val = self.prior_context[self.varname(net.args[1])]
                write_enable = self.prior_context[self.varname(net.args[2])]
                if write_enable:
                    self.context['fastsim_mem'][(memid, write_addr)] = write_val

        # update inputs
        for wire, value in provided_inputs.items():
            self.context[self.varname(wire)] = wire.bitmask & value

        # propagate through logic
        exec(self.logic_function, self.context)

        if self.tracer is not None:
            self.tracer.add_fast_step(self)

    def inspect(self, thing):
        """ Get the value of 'thing' in the current simulation cycle. """
        return self.context[self.varname(thing)]

    @staticmethod
    def varname(val):
        # TODO check if w.name is a legal python identifier
        if isinstance(val, _MemReadBase):
            return 'fs_mem' + str(val.id)
        else:
            return val.name

    def compiled(self):
        """Return a string of the self.block compiled to python. """
        prog = ''

        simple_func = {  # OPS
            'w': lambda x: x,
            '~': lambda x: '(~' + x + ')',
            '&': lambda l, r: '(' + l + '&' + r + ')',
            '|': lambda l, r: '(' + l + '|' + r + ')',
            '^': lambda l, r: '(' + l + '^' + r + ')',
            'n': lambda l, r: '(~(' + l + '&' + r + '))',
            '+': lambda l, r: '(' + l + '+' + r + ')',
            '-': lambda l, r: '(' + l + '-' + r + ')',
            '*': lambda l, r: '(' + l + '*' + r + ')',
            '<': lambda l, r: 'int(' + l + '<' + r + ')',
            '>': lambda l, r: 'int(' + l + '>' + r + ')',
            '=': lambda l, r: 'int(' + l + '==' + r + ')',
            'x': lambda sel, a, b: '({}) if ({}==0) else ({})'.format(a, sel, b),
            }

        for net in self.block:
            prog += '#  ' + str(net) + '\n'
            if net.op in simple_func:
                argvals = (self.varname(arg) for arg in net.args)
                result = simple_func[net.op](*argvals)
                mask = str(net.dests[0].bitmask)
                prog += self.varname(net.dests[0]) + ' = ' + mask + ' & ' + result + '\n'
            elif net.op == 'c':
                result = self.varname(net.dests[0])
                mask = str(net.dests[0].bitmask)
                expr = ''
                for i in range(len(net.args)):
                    if expr is not '':
                        expr += ' | '
                    shiftby = str(sum(len(net.args[j]) for j in range(i+1, len(net.args))))
                    expr += '(%s << %s)' % (self.varname(net.args[i]), shiftby)
                prog += '%s = %s & (%s)\n' % (result, mask, expr)
            elif net.op == 's':
                source = self.varname(net.args[0])
                result = self.varname(net.dests[0])
                mask = str(net.dests[0].bitmask)
                expr = ''
                i = 0
                for b in net.op_param:
                    if expr is not '':
                        expr += ' | '
                    bit = '(0x1 & (%s >> %d))' % (source, b)
                    expr += '(%s << %d)' % (bit, i)
                    i += 1
                prog += '%s = %s & (%s)\n' % (result, mask, expr)

            elif net.op == 'm':
                read_addr = self.varname(net.args[0])
                mask = str(net.dests[0].bitmask)
                result = self.varname(net.dests[0])

                if isinstance(net.op_param[1], RomBlock):
                    expr = '%s._get_read_data(%s)' % (self.varname(net.op_param[1]), read_addr)
                else:
                    # memories act async for reads
                    memid = net.op_param[0]
                    index = '(%d, %s)' % (memid, read_addr)
                    expr = 'fastsim_mem.get(%s, %s)' % (index, self.default_value)

                prog += '%s = %s & %s\n' % (result, mask, expr)

            elif net.op == 'r' or net.op == '@':
                pass  # registers and memory write ports have no logic function
            else:
                raise PyrtlError('FastSimulation cannot handle primitive "%s"' % net.op)

        return prog


# ----------------------------------------------------------------
#    ___  __        __   ___
#     |  |__)  /\  /  ` |__
#     |  |  \ /~~\ \__, |___
#

class _WaveRendererBase(object):
    _tick, _up, _down, _x, _low, _high, _revstart, _revstop = ('' for i in range(8))

    def __init__(self):
        super(_WaveRendererBase, self).__init__()
        self.prior_val = None
        self.prev_wire = None

    def tick_segment(self, n, symbol_len, segment_size):
        num_tick = self._tick + str(n)
        return num_tick.ljust(symbol_len * segment_size)

    def render_val(self, w, n, current_val, symbol_len):
        if w is not self.prev_wire:
            self.prev_wire = w
            self.prior_val = current_val
        out = self._render_val_with_prev(w, n, current_val, symbol_len)
        self.prior_val = current_val
        return out

    def _render_val_with_prev(self, w, n, current_val, symbol_len):
        """Return a string encoding the given value in a waveform.

        :param w: The WireVector we are rendering to a waveform
        :param n: An integer from 0 to segment_len-1
        :param current_val: the value to be rendered
        :param symbol_len: and integer for how big to draw the current value

        Returns a string of printed length symbol_len that will draw the
        representation of current_val.  The input prior_val is used to
        render transitions.
        """
        sl = symbol_len-1
        if len(w) > 1:
            out = self._revstart
            if current_val != self.prior_val:
                out += self._x + hex(current_val).rstrip('L').ljust(sl)[:sl]
            elif n == 0:
                out += hex(current_val).rstrip('L').ljust(symbol_len)[:symbol_len]
            else:
                out += ' '*symbol_len
            out += self._revstop
        else:
            pretty_map = {
                (0, 0): self._low + self._low * sl,
                (0, 1): self._up + self._high * sl,
                (1, 0): self._down + self._low * sl,
                (1, 1): self._high + self._high * sl,
            }
            out = pretty_map[(self.prior_val, current_val)]
        return out


class Utf8WaveRenderer(_WaveRendererBase):
    _tick = u'\u258f'
    _up, _down = u'\u2571', u'\u2572'
    _x, _low, _high = u'\u2573', u'\u005f', u'\u203e'
    _revstart, _revstop = '\x1B[7m', '\x1B[0m'


class AsciiWaveRenderer(_WaveRendererBase):
    """ Poor Man's wave renderer (for windows cmd compatibility)"""
    _tick = '-'
    _up, _down = '/', '\\'
    _x, _low, _high = 'x', '_', '-'
    _revstart, _revstop = ' ', ' '


def default_renderer():
    import sys
    try:
        if str(sys.stdout.encoding).lower() == "utf-8":
            return Utf8WaveRenderer
    except Exception:
        pass
    return AsciiWaveRenderer


def _trace_sort_key(w):
    def tryint(s):
        try:
            return int(s)
        except ValueError:
            return s
    return [tryint(c) for c in re.split('([0-9]+)', w.name)]


class SimulationTrace(object):
    """ Storage and presentation of simulation waveforms. """

    def __init__(self, wirevector_subset=None, block=None):
        block = working_block(block)

        def is_internal_name(name):
            return (name.startswith('tmp') or name.startswith('const') or
                    # or name.startswith('synth_')
                    name.endswith("'"))

        if wirevector_subset is None:
            self.trace = {
                w: []
                for w in block.wirevector_set
                if not is_internal_name(w.name)
                }
        elif wirevector_subset == 'all':
            self.trace = {w: [] for w in block.wirevector_set}
        else:
            self.trace = {w: [] for w in wirevector_subset}

    def __len__(self):
        """ Return the current length of the trace in cycles. """
        if len(self.trace) == 0:
            raise PyrtlError('error, length of trace undefined if no signals tracked')
        # return the length of the list of some element in the dictionary (all should be the same)
        wire, value_list = next(x for x in self.trace.items())
        return len(value_list)

    def add_step(self, value_map):
        """ Add the values in value_map to the end of the trace. """
        if len(self.trace) == 0:
            raise PyrtlError('error, simulation trace needs at least 1 signal '
                             'to track (try passing name to WireVector)')
        for wire in self.trace:
            self.trace[wire].append(value_map[wire])

    def add_fast_step(self, fastsim):
        """ Add the fastsim context to the trace. """
        for w in self.trace:
            self.trace[w].append(fastsim.context[fastsim.varname(w)])

    def print_trace(self, file=sys.stdout):
        if len(self.trace) == 0:
            raise PyrtlError('error, cannot print an empty trace')
        maxlen = max([len(w.name) for w in self.trace])
        for w in sorted(self.trace, key=_trace_sort_key):
            file.write(' '.join([w.name.rjust(maxlen),
                       ''.join(str(x) for x in self.trace[w])+'\n']))
            file.flush()

    def print_vcd(self, file=sys.stdout):
        """ Print the trace out as a VCD File for use in other tools. """
        # dump header info
        # file_timestamp = time.strftime("%a, %d %b %Y %H:%M:%S (UTC/GMT)", time.gmtime())
        # print >>file, " ".join(["$date", file_timestamp, "$end"])
        print(' '.join(['$timescale', '1ns', '$end']), file=file)
        print(' '.join(['$scope', 'module logic', '$end']), file=file)

        def print_trace_strs(time):
            for w in sorted(self.trace, key=_trace_sort_key):
                if w.bitwidth > 1:
                    print(' '.join([str(bin(self.trace[w][time]))[1:], w.name]), file=file)
                else:
                    print(''.join([str(self.trace[w][time]), w.name]), file=file)

        # dump vairables
        for w in sorted(self.trace, key=_trace_sort_key):
            print(' '.join(['$var', 'wire', str(w.bitwidth), w.name, w.name, '$end']), file=file)
        print(' '.join(['$upscope', '$end']), file=file)
        print(' '.join(['$enddefinitions', '$end']), file=file)
        print(' '.join(['$dumpvars']), file=file)
        print_trace_strs(0)
        print(' '.join(['$end']), file=file)

        # dump values
        endtime = max([len(self.trace[w]) for w in self.trace])
        for timestamp in range(endtime):
            print(''.join(['#', str(timestamp)]), file=file)
            print_trace_strs(timestamp)
        print(''.join(['#', str(endtime)]), file=file)
        file.flush()

    def render_trace(
            self, trace_list=None, file=sys.stdout, render_cls=default_renderer(),
            symbol_len=5, segment_size=5, segment_delim=' ', extra_line=True):
        """ Render the trace to a file using unicode and ASCII escape sequences.

        The resulting output can be viewed directly on the terminal or looked
        at with "more" or "less -R" which both should handle the ASCII escape
        sequences used in rendering. render_trace takes the following optional
        arguments.
        :param trace_list: A list of signals to be output in the specified order.
        :param file: The place to write output, default to stdout.
        :param render_cls: A class that translates traces into output bytes.
        :param symbol_len: The "length" of each rendered cycle in characters.
        :param segment_size: Traces are broken in the segments of this number of cycles.
        :param segment_delim: The character to be output between segments.
        :param extra_line: A Boolean to determin if we should print a blank line between signals.
        """
        renderer = render_cls()

        def formatted_trace_line(wire, trace):
            heading = wire.name.rjust(maxnamelen) + ' '
            trace_line = ''
            for i in range(len(trace)):
                if (i % segment_size == 0) and i > 0:
                    trace_line += segment_delim
                trace_line += renderer.render_val(wire, i % segment_size, trace[i], symbol_len)
            return heading + trace_line

        # default to printing all signals in sorted order
        if trace_list is None:
            trace_list = sorted(self.trace, key=_trace_sort_key)

        # print the 'ruler' which is just a list of 'ticks'
        # mapped by the pretty map

        maxnamelen = max(len(w.name) for w in self.trace)
        maxtracelen = max(len(v) for v in self.trace.values())
        if segment_size is None:
            segment_size = maxtracelen
        spaces = ' '*(maxnamelen+1)
        ticks = [renderer.tick_segment(n, symbol_len, segment_size)
                 for n in range(0, maxtracelen, segment_size)]
        print(spaces + segment_delim.join(ticks), file=file)

        # now all the traces
        for w in trace_list:
            if extra_line:
                print(file=file)
            print(formatted_trace_line(w, self.trace[w]), file=file)
        if extra_line:
            print(file=file)
