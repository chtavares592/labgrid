# pylint: disable=no-member
import subprocess
import attr
import time

from ..factory import target_factory
from ..protocol import BootstrapProtocol
from ..resource.remote import NetworkMXSUSBLoader, NetworkIMXUSBLoader, NetworkRKUSBLoader
from ..resource.udev import MXSUSBLoader, IMXUSBLoader, RKUSBLoader
from ..step import step
from .common import Driver
from ..util.managedfile import ManagedFile


@target_factory.reg_driver
@attr.s(cmp=False)
class MXSUSBDriver(Driver, BootstrapProtocol):
    bindings = {
        "loader": {MXSUSBLoader, NetworkMXSUSBLoader},
    }

    image = attr.ib(default=None)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # FIXME make sure we always have an environment or config
        if self.target.env:
            self.tool = self.target.env.config.get_tool('mxs-usb-loader') or 'mxs-usb-loader'
        else:
            self.tool = 'mxs-usb-loader'

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    @Driver.check_active
    @step(args=['filename'])
    def load(self, filename=None):
        if filename is None and self.image is not None:
            filename = self.target.env.config.get_image_path(self.image)
        mf = ManagedFile(filename, self.loader)
        mf.sync_to_resource()

        subprocess.check_call(
            self.loader.command_prefix+[self.tool, "0", mf.get_remote_path()]
        )


@target_factory.reg_driver
@attr.s(cmp=False)
class IMXUSBDriver(Driver, BootstrapProtocol):
    bindings = {
        "loader": {IMXUSBLoader, NetworkIMXUSBLoader, MXSUSBLoader, NetworkMXSUSBLoader},
    }

    image = attr.ib(default=None)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # FIXME make sure we always have an environment or config
        if self.target.env:
            self.tool = self.target.env.config.get_tool('imx-usb-loader') or 'imx-usb-loader'
        else:
            self.tool = 'imx-usb-loader'

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    @Driver.check_active
    @step(args=['filename'])
    def load(self, filename=None):
        if filename is None and self.image is not None:
            filename = self.target.env.config.get_image_path(self.image)
        mf = ManagedFile(filename, self.loader)
        mf.sync_to_resource()

        subprocess.check_call(
            self.loader.command_prefix +
            [self.tool, "-p", str(self.loader.path), "-c", mf.get_remote_path()]
        )


@target_factory.reg_driver
@attr.s(cmp=False)
class RKUSBDriver(Driver, BootstrapProtocol):
    bindings = {
        "loader": {RKUSBLoader, NetworkRKUSBLoader},
    }

    image = attr.ib(default=None)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # FIXME make sure we always have an environment or config
        if self.target.env:
            self.tool = self.target.env.config.get_tool('rk-usb-loader') or 'rk-usb-loader'
        else:
            self.tool = 'rk-usb-loader'

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    @Driver.check_active
    @step(args=['filename'])
    def load(self, filename=None):
        # FIXME make sure we always have an environment or config
        loaders = self.target.env.config.get_tool('loader') or 'loader'
        mf = ManagedFile(loaders, self.loader)
        mf.sync_to_resource()

        subprocess.check_call(
            self.loader.command_prefix
            + [self.tool, 'db', mf.get_remote_path()]
        )

        if filename is None and self.image is not None:
            filename = self.target.env.config.get_image_path(self.image)
        mf = ManagedFile(filename, self.loader)
        mf.sync_to_resource()

        # wait the loader finish the process
        time.sleep(1)

        # The u-boot image is written on the device
        subprocess.check_call(
            self.loader.command_prefix +
            [self.tool, 'wl', '0x40', mf.get_remote_path()]
        )
