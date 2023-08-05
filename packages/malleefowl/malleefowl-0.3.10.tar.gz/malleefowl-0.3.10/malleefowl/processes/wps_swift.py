from pywps.Process import WPSProcess

import tempfile

from malleefowl import swiftcloud
from malleefowl import config

class SwiftLogin(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="swift_login",
            title="Login to Swift Cloud",
            version="0.2",
            abstract="Login to Swift Cloud and get Token.",
            storeSupported=True,
            statusSupported=True)

        self.auth_url = self.addLiteralInput(
            identifier="auth_url",
            title="Auth URL",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.auth_version = self.addLiteralInput(
            identifier="auth_version",
            title="Auth Version",
            minOccurs=1,
            maxOccurs=1,
            default=1,
            allowedValues=[1,2],
            type=type(1),
            )

        self.username = self.addLiteralInput(
            identifier="username",
            title="Username",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.password = self.addLiteralInput(
            identifier = "password",
            title = "Password",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.auth_token = self.addLiteralOutput(
            identifier="auth_token",
            title="Auth Token",
            type=type(''),
            )

        self.storage_url = self.addLiteralOutput(
            identifier="storage_url",
            title="Storage URL",
            type=type(''),
            )

    def execute(self):
        (storage_url, auth_token) = swiftcloud.login(
            self.username.getValue(),
            self.password.getValue(),
            auth_url = self.auth_url.getValue(),
            auth_version = self.auth_version.getValue())

        self.storage_url.setValue( storage_url )
        self.auth_token.setValue( auth_token )

class SwiftDownload(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "swift_download",
            title = "Download files from Swift Cloud",
            version = "0.2",
            abstract="Downloads files from Swift Cloud and provides file List as JSON Document.",
            statusSupported=True,
            storeSupported=True)

        self.storage_url = self.addLiteralInput(
            identifier="storage_url",
            title="Storage URL",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.auth_token = self.addLiteralInput(
            identifier = "auth_token",
            title = "Auth Token",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )       

        self.container = self.addLiteralInput(
            identifier = "container",
            title = "Container",
            abstract = "Container",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.prefix = self.addLiteralInput(
            identifier = "prefix",
            title = "Prefix",
            abstract = "Example: test/subfolder",
            minOccurs=0,
            maxOccurs=1,
            type=type(''),
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Downloaded files",
            abstract="JSON document with list of downloaded files with file url.",
            metadata=[],
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        files = swiftcloud.download(
            self.storage_url.getValue(),
            self.auth_token.getValue(),
            self.container.getValue(),
            self.prefix.getValue())

        import json
        _,outfile = tempfile.mkstemp(suffix='.json')
        with open(outfile, 'w') as fp:
            json.dump(obj=files, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( outfile )


class SwiftDownloadUrls(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "swift_download_urls",
            title = "Provide download URLs for files from Swift Cloud",
            version = "0.2",
            abstract="Provide download URLs for files from Swift Cloud and return url list as json document.",
            statusSupported=True,
            storeSupported=True)

        self.storage_url = self.addLiteralInput(
            identifier="storage_url",
            title="Storage URL",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.auth_token = self.addLiteralInput(
            identifier = "auth_token",
            title = "Auth Token",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.container = self.addLiteralInput(
            identifier = "container",
            title = "Container",
            abstract = "Container",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.prefix = self.addLiteralInput(
            identifier = "prefix",
            title = "Prefix",
            abstract = "Example: test/subfolder",
            minOccurs=0,
            maxOccurs=1,
            type=type(''),
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Downloaded files",
            abstract="JSON document with list of downloaded files with file url.",
            metadata=[],
            formats=[{"mimeType":"test/json"}],
            asReference=True,
            )

    def execute(self):
        files = swiftcloud.download_urls(
            self.storage_url.getValue(),
            self.auth_token.getValue(),
            self.container.getValue(),
            self.prefix.getValue())

        import json
        _,outfile = tempfile.mkstemp(suffix='.json')
        with open(outfile, 'w') as fp:
            json.dump(obj=files, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( outfile )

class SwiftUpload(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="swift_upload",
            title="Upload files to Swift Cloud",
            version="0.2",
            abstract="Upload files to Swift Cloud and provides upload status as JSON Document.",
            statusSupported=True,
            storeSupported=True)

        self.storage_url = self.addLiteralInput(
            identifier="storage_url",
            title="Storage URL",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.auth_token = self.addLiteralInput(
            identifier = "auth_token",
            title = "Auth Token",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )       

        self.container = self.addLiteralInput(
            identifier = "container",
            title = "Container",
            abstract = "Container",
            minOccurs=1,
            maxOccurs=1,
            type=type(''),
            )

        self.prefix = self.addLiteralInput(
            identifier = "prefix",
            title = "Prefix",
            abstract = "Example: test/subfolder",
            minOccurs=0,
            maxOccurs=1,
            type=type(''),
            )

        self.resource = self.addComplexInput(
            identifier="resource",
            title="Files",
            abstract="Files to upload",
            minOccurs=0,
            maxOccurs=1024,
            maxmegabites=50000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Status",
            abstract="JSON document with list of upload status",
            metadata=[],
            formats=[{"mimeType":"test/json"}],
            asReference=True,
            )

    def execute(self):
        result = swiftcloud.upload(
            storage_url = self.storage_url.getValue(),
            auth_token = self.auth_token.getValue(),
            container = self.container.getValue(),
            prefix = self.prefix.getValue(),
            files = getInputValues(self, identifier='resource'),
            monitor = self.status.set)

        import json
        _, outfile = tempfile.mkstemp(suffix='.json')
        with open(outfile, 'w') as fp:
            json.dump(obj=result, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( outfile )
