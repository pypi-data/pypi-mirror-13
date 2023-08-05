from paramSeeker import ParamSeeker, __version__

seeker = ParamSeeker()

# add usage
seeker.set_usage_desc("seeker [OPTION]... ")
seeker.set_usage_desc('seeker thing')

seeker.set_desc("this is like a demo to tell how to use this package\n" +
                "also, this is my test project, with the name of seek\n" +
                "which is sick to see the source code, but the code is\n" +
                "at your source code dir, and you can visit\n\n" +
                "https://github.com/hellflame/paramSeeker/blob/master/seeker/example.py\n" +
                "reference at http://hellflame.github.io/doc/paramSeeker-doc/")


@seeker.seek('--linux', short='-l', extra={'desc': 'this is a test function', 'single_param': True})
def first(wanted):
    result = '\nthis is the first test method and it has got the argument \n\t`\033[01;31m{}\033[00m`\n'.\
        format(wanted)
    return result


@seeker.seek('--black', short='-b', extra={'desc': 'this is a test function with the param head black'})
def second(wanted):
    result = '\nthis is the second test method and it has got the argument \n\t`\033[01;33m{}\033[00m`\n'.\
        format(wanted)
    return result


@seeker.seek('--tell', short='-t', is_mark=True, extra={'desc': 'I may tell you something'})
def tell(wanted):
    return "Well, if you really want to know, I really may release this example as A little tool ~~~"


@seeker.seek('--version', short='-v', is_mark=True, extra={'desc': 'version info'})
def version_teller(wanted):
    """it is not recommended to exit like this, but if you are pretty sure there won't be
    any thing to execute next"""
    print(__version__)
    exit(0)


@seeker.seek()
def final(wanted):
    result = "Well ~~~ you got `\033[01;31m{}\033[00m`".format(wanted)
    return result


@seeker.seek('--default', short='-d', extra={'default': 'default value'})
def default(wanted):
    my_own_value = wanted
    if wanted == 'default value':
        return "Here you will have the default value `\033[01;34m{}\033[00m`".format(wanted)
    else:
        return "Here you got another value `\033[01;34m{}\033[00m`".format(wanted)


def test_env():
    seeker.run()

if __name__ == '__main__':
    test_env()

