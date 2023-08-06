import os

from . import Device
from ..streams import InputStream, OutputStream

class Terminal(Device):
  def __init__(self, machine, name, echo = False, *args, **kwargs):
    super(Terminal, self).__init__(machine, 'terminal', name, *args, **kwargs)

    self.input = None
    self.output = None

    self.echo = echo
    self._input_read_u8_orig = None

  def _input_read_u8_echo(self, *args, **kwargs):
    c = self._input_read_u8_orig(*args, **kwargs)

    if c != 0xFF:
      self.output.write_u8(self.output.port, c)

    return c

  def patch_echo(self, restore = False):
    D = self.machine.DEBUG

    D('%s.patch_echo: echo=%s, restore=%s', self.__class__.__name__, self.echo, restore)

    if restore is True and self._input_read_u8_orig is not None:
      self.input.read_u8, self._input_read_u8_orig = self._input_read_u8_orig, None

    elif self.echo is True:
      assert self.input is not None
      assert hasattr(self.input, 'read_u8')
      assert hasattr(self.output, 'write_u8')

      self._input_read_u8_orig, self.input.read_u8 = self.input.read_u8, self._input_read_u8_echo

    D('%s.patch_echo: input.read_u8=%s, orig_input.read_u8=%s', self.__class__.__name__, self.input.read_u8, self._input_read_u8_orig)

  def boot(self):
    super(Terminal, self).boot()

    self.patch_echo()

  def halt(self):
    super(Terminal, self).halt()

    self.patch_echo(restore = True)

def parse_io_streams(machine, config, section):
  streams_in, stream_out = None, None

  if config.has_option(section, 'streams_in'):
    streams_in = [InputStream.create(machine.LOGGER, e.strip()) for e in config.get(section, 'streams_in').split(',')]

  if config.has_option(section, 'stream_out'):
    stream_out = OutputStream.create(machine.LOGGER, config.get(section, 'stream_out'))

  return (streams_in, stream_out)

def get_slave_devices(machine, config, section):
  input_name = config.get(section, 'input', None)
  input_device = machine.get_device_by_name(input_name)

  if not input_name or not input_device:
    machine.ERROR('Unknown slave device %s', input_name)

  output_name = config.get(section, 'output', None)
  output_device = machine.get_device_by_name(output_name)

  if not output_name or not output_device:
    machine.ERROR('Unknown slave device %s', output_name)

  return (input_device, output_device)

class StreamIOTerminal(Terminal):
  def __init__(self, machine, name, input = None, output = None, *args, **kwargs):
    super(StreamIOTerminal, self).__init__(machine, name, *args, **kwargs)

    self.input = input
    self.output = output

    self.input.master = self
    self.output.master = self

  def enqueue_input_stream(self, stream):
    self.input.enqueue_input(stream)

  def enqueue_streams(self, streams_in = None, stream_out = None):
    self.machine.DEBUG('%s.enqueue_streams: streams_in=%s, stream_out=%s', self.__class__.__name__, streams_in, stream_out)

    if streams_in is not None:
      streams_in = streams_in or []

      for stream in streams_in:
        self.enqueue_input_stream(stream)

    if stream_out is not None:
      self.output.set_output(stream_out)

  @staticmethod
  def create_from_config(machine, config, section):
    input_device, output_device = get_slave_devices(machine, config, section)

    term = StreamIOTerminal(machine, section, input = input_device, output = output_device, echo = config.getbool(section, 'echo', False))

    streams_in, stream_out = parse_io_streams(machine, config, section)
    term.enqueue_streams(streams_in = streams_in, stream_out = stream_out)

    return term

  def boot(self):
    self.machine.DEBUG('StreamIOTerminal.boot')

    super(StreamIOTerminal, self).boot()

    self.input.boot()
    self.output.boot()

    self.machine.INFO('hid: basic terminal (%s, %s)', self.input.name, self.output.name)

  def halt(self):
    self.machine.DEBUG('StreamIOTerminal.halt')

    super(StreamIOTerminal, self).halt()

    self.input.halt()
    self.output.halt()

    self.machine.DEBUG('Standard terminal halted.')

class StandardIOTerminal(StreamIOTerminal):
  @staticmethod
  def create_from_config(machine, config, section):
    input_device, output_device = get_slave_devices(machine, config, section)

    term = StandardIOTerminal(machine, section, input = input_device, output = output_device)
    term.enqueue_streams(streams_in = [InputStream.create(machine.LOGGER, '<stdin>')], stream_out = OutputStream.create(machine.LOGGER, '<stdout>'))

    return term

class StandalonePTYTerminal(StreamIOTerminal):
  def __init__(self, *args, **kwargs):
    super(StandalonePTYTerminal, self).__init__(*args, **kwargs)

    self.pttys = None

  @staticmethod
  def create_from_config(machine, config, section):
    input_device, output_device = get_slave_devices(machine, config, section)

    term = StandalonePTYTerminal(machine, section, input = input_device, output = output_device, echo = config.getbool(section, 'echo', False))

    streams_in, stream_out = parse_io_streams(machine, config, section)
    term.enqueue_streams(streams_in = streams_in, stream_out = stream_out)

    return term

  def boot(self):
    self.machine.DEBUG('StandalonePTYTerminal.boot')

    Terminal.boot(self)

    if self.pttys is not None:
      return

    import pty

    pttys = pty.openpty()

    self.machine.DEBUG('  set I/O stream: pttys=%s', pttys)

    self.enqueue_streams(streams_in = [InputStream.create(self.machine.LOGGER, pttys[0])], stream_out = OutputStream.create(self.machine.LOGGER, pttys[0]))

    self.terminal_device = os.ttyname(pttys[1]) if pttys else '/dev/unknown'

    self.input.boot()
    self.output.boot()

    self.pttys = pttys

    self.machine.INFO('hid: pty terminal (%s, %s), dev %s', self.input.name, self.output.name, self.terminal_device)

  def halt(self):
    self.machine.DEBUG('StandalonePTYTerminal.halt')

    Terminal.halt(self)

    if self.pttys is None:
      return

    self.input.halt()
    self.output.halt()

    try:
      os.close(self.pttys[1])
      os.close(self.pttys[0])

      self.pttys = None
      self.terminal_device = None

    except Exception:
      self.machine.EXCEPTION('Exception raised while closing PTY')

    self.machine.DEBUG('StandalonePTYTerminal: halted')
