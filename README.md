# Sublime Text 3 Perforce Plugin

Supports auto add and checkout with commands to add, checkout, delete, diff, rename, revert, diff using p4diff and lists all checked out files with quick access to them with simple changelist management.

## Install

The preferred method is to use the [Sublime Package Manager](http://wbond.net/sublime_packages/package_control). Alternatively, the files can be obtained on github:

    $ https://github.com/ericmartel/Sublime-Text-3-Perforce-Plugin
    
Once you have downloaded the plugin into Sublime, you need to ensure the plugin knows your P4 details.  You have two options, either to set the required variables on the command line

    > p4 set P4CLIENT=workspace_name
    > p4 set P4PORT=my.perforceserver.com:1666
    > p4 set P4USER=myusername 

You can also place a P4CONFIG in your workspace root and it will load from there.

You can then login to perforce from the Tools|Perforce|Login command.
    
### Install Note

If the plugin is unable to use your p4, it is possible that it keeps reporting that the file is not under the client root.  User @JLoppert suggests creating a symlink under OSX/Linux

    sudo ln -s /usr/bin/local/p4 /usr/bin/p4

## Complete Documentation

A website is currently under construction to explain the usage of the plugin in details. In the meantime, please visit this [Web Site](http://www.ericmartel.com/sublime-text-3-perforce-plugin/).

# License

All of Sublime Text 3 Perforce Plugin is licensed under the MIT license.

Copyright (c) 2013 Eric Martel <emartel@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
