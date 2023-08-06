import argparse


// mozci-trigger --rev 5f6ca9194dd9 -b "Rev4 MacOSX Snow Leopard 10.6 try opt test mochitest-browser-chrome-2" --file https://ftp.mozilla.org/pub/mozilla.org/firefox/try-builds/mozilla@noorenberghe.ca-5f6ca9194dd9/try-macosx64/firefox-41.0a1.en-US.mac.dmg --file https://people.mozilla.org/~mnoorenberghe/tmp/screenshots_mbc2.tests.zip

platforms = {
    "10.6": {
        
    }
}

parser = argparse.ArgumentParser(description="Run mozscreenshots on Try server")
parser.add_argument("--10.6", action="store_true")
args = parser.parse_args()
print dir(args)
print getattr(args, "10.6")




