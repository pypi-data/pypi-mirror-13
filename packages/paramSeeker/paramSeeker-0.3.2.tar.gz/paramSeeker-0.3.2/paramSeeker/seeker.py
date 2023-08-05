from sys import argv


class ParamSeeker:
    def __init__(self, prefix='--', prefix_short='-'):
        """Things you should know, prefix and prefix_short are used to get the argument
        change the two param cautiously !!
        It is not recommended to make change !!

        ! NOTICE:
            below I may use `seeker` for example
            `seeker` is a console application which will be installed as you `pip install`
            delete it if you don't like it

            if you see `youdao`
            it's a console application too ... which is still in use

        :param prefix   (string)
            define the full argument start
            default '--'
        :param prefix_short (string)
            define the short term of the argument
            default '-'
        """
        self.args = argv[1:]
        self.arg_len = len(self.args)
        self.collection = {}
        self.prefix = prefix
        self.prefix_short = prefix_short
        self.usage_desc = ''
        self.desc = ''
        self.no_head_bind = {}
        self.has_input = False

    def set_usage_desc(self, desc):
        """Set the usage description, you can use this for more than one time,
        it works on your help menu
        :param desc (string)
                descriptions for the current usage declare
                display auto decided
                example:
                    app.set_usage_desc(desc="seeker [OPTION]...")

        """
        self.usage_desc += '\t' + desc + '\n'

    def set_desc(self, desc):
        """
        :param desc (string)
                description for the whole project
                multiple use will merge, it works on your help menu

                example:

                    app.set_desc("tell you what does the word mean")

                        You can deploy this method at anyplace,
                    but before you deploy `app.run()`
        """
        self.desc = desc

    def __param_desc_full(self):
        """I don't want users to care about this part,
        I don't want to care about this in my own apps either
        but you have your own way to access this part I know"""
        result = ''
        for group in self.collection:
            result += group.strip() + ' options:\n'
            for args in self.collection[group]:
                result += self.__param_desc(args)
        return result

    @staticmethod
    def __param_desc(args):
        """I don't want users to care about this part,
        I don't want to care about this in my own apps either
        but you have your own way to access this part I know"""
        result = ''
        if args['short']:
            result += args['short'] + ', '
        result += args['param'] + '\t'
        result += args['desc']
        result += '\n'
        return result

    def print_help(self, redundancy=None):
        """Print help menu
            :param redundancy
                (you won't use)   just as a redundancy :) No used or useless,
                just to make the application run correctly.....
        """
        print("""Usage: \n{usage}\n{total_desc}\n\n{param_desc}""".format(
            usage=self.usage_desc,
            total_desc=self.desc,
            param_desc=self.__param_desc_full()))
        exit(0)

    def get_full_param(self, param=None, single_param=True, is_mark=False):
        """Get the target according to the full require
            :param param          (string)
                                    actually this is the param head (too lazy to change the name orz)
                                    example:
                                        $ youdao --word fox

                                        Here '--word' is what I mean the 'param' , the full state
                                        if the param is None, it will return first several param
                                        in the console

                                        $ youdao fox

                                        Then, 'linux' will be seen as a no param head param,
                                        only one method is allowed to be attached to it,
                                        if more than one method is given, merge you will know


            :param single_param   (bool)
                                    whether or not continues to see the following as the param
                                    example:
                                        $ youdao --word linux is best

                                        Here if the 'single_param' is True:
                                            which actually means:
                                                $ youdao --word 'linux is best'
                                        else:
                                            which just mean:
                                                $ youdao --word 'linux'

            :param is_mark         (bool)
                                            whether the param head used ad a mark only
                                            example:
                                                $ youdao linux --trans

                                            Here '--trans' is used as a mark only, which means its existence
                                             is what I care
        """
        if is_mark and param in self.args:
            return True
        result = ''
        if not param:
            for i in self.args:
                if not i.startswith(self.prefix) and not i.startswith(self.prefix_short):
                    result += i + ' '
                else:
                    break
            return result.strip()
        if param not in argv:
            return False

        last = argv[argv.index(param):]
        if len(last) > 1:
            if single_param:
                return argv[argv.index(param) + 1]
            for i in argv[argv.index(param) + 1:]:
                if not i.startswith(self.prefix) and not i.startswith(self.prefix_short):
                    result += i + ' '
                else:
                    break
            return result.strip()
        return False

    def get_short_param(self, short_param=None, single_param=True, is_mark=False):
        """Get the target according to the short require
            :param short_param (string)
                    well, actually this most functions like the `get_full_param`, but I prefer to make a difference
                this param is more likely to be `-b` or `-l`, in this case, this method support a kind match like
                when give `-nutpl` and `-l` is a mark (is_mark=True)
                    `-l` will be regard as True
            :param single_param (bool)
                    whether or not continues to see the following as the param
                example will be seen at `get_full_param` but in short term
            :param is_mark  (bool)
                    whether the param head used ad a mark only
                example will be seen at `get_full_param` but in short term
        """
        if is_mark:
            if short_param in self.args:
                return True
            if short_param.startswith(self.prefix_short) and self.args:
                from re import compile
                regs = compile('(?<={})\w'.format(self.prefix_short))
                target = regs.findall(short_param)[0]
                for param in self.args:
                    if param.startswith(self.prefix_short) and \
                            not param.startswith(self.prefix) and \
                            target in param:
                        return True

        if short_param not in argv:
            return False

        last = argv[argv.index(short_param):]
        if len(last) > 1:
            if single_param:
                return argv[argv.index(short_param) + 1]
            result = ''
            for single in argv[argv.index(short_param) + 1:]:
                if not single.startswith(self.prefix) and not single.startswith(self.prefix_short):
                    result += single + ' '
                else:
                    break
            return result.strip()
        return False

    def seek(self, param='', short='', is_mark=False, extra={}):
        """A decorator used to bind the param and its dealing method

                @app.seek('human', extra={'param_short':'h'})
                def human(wanted):
                    return 'this is human readable result'

                    Here the param 'wanted' will be the argument from the console,
                you can deal with it with your own 'human' method

        example:
                    if param='human'
                    then extra may be like:
                    {
                        'group':'General',
                        'desc':'human readable feed back',
                        'single_param':False
                    }

        :param param (string)
                the argument(s) you want to get by
        :param short (string)
                short term of your argument
        :param is_mark (bool)
                whether or not allow ZERO argument which means the param is
                used as a mark
        :param extra (dict)
                extra info to confirm your desire
                options:
                    :arg group          (string)    which group to belong
                    :arg desc           (string)    description of the param
                    :arg single_param   (bool)      whether the wanted result single argument or multiple
                                                    $ youdao -w linux is fine -c ok

                                                    if single_param:
                                                        which means
                                                        $ youdao -w linux -c ok
                                                    else:
                                                        which means as it receives
                    :arg default        (string)        if default value is set and no more input is given
                                                    your method will receive this value, be careful with the
                                                    option, no matter you enter or not, it will have one value
                                                    suggest the method return '' (null string) or you can make
                                                    your own decision like example
                                                    ! NOTICE
                                                    when you test with

                                                        $ seeker --linux
                                                        > Here you will have the default value `default value`
                                                    it's not because the program went wrong, this is the out put from

                                                        $ seeker --default
        """
        def seek_wrap(wrapped):
            result = self.get_full_param(param=param,
                                         single_param=extra.get('single_param', False),
                                         is_mark=is_mark) \
                     or self.get_short_param(short_param=short,
                                             single_param=extra.get('single_param', False),
                                             is_mark=is_mark)
            # deal with param without head
            if not param:
                if not result and extra.get('default', False):
                    self.no_head_bind['wanted'] = extra.get('default')
                else:
                    self.no_head_bind['wanted'] = result

                self.no_head_bind['bind_method'] = wrapped
                return wrapped
            target = {
                'param': param,
                'short': short,
                'desc': extra.get('desc', '')
            }
            if not result and extra.get('default', False):
                target['wanted'] = extra.get('default')
            else:
                target['wanted'] = result

            group = extra.get('group', 'General')

            target['bind_method'] = wrapped

            if group not in self.collection:
                self.collection[group] = []
            self.collection[group].append(target)
            return wrapped
        return seek_wrap

    def bind_help(self):
        result = self.get_full_param(param='--help',
                                     single_param=True,
                                     is_mark=True) or \
                 self.get_short_param(short_param='-h',
                                      single_param=True,
                                      is_mark=True)
        target = {
            'param': '--help',
            'short': '-h',
            'desc': 'help',
            'wanted': result,
            'bind_method': self.print_help
        }
        if 'General' not in self.collection:
            self.collection['General'] = []
        self.collection['General'].append(target)

    @staticmethod
    def execute(func, args):
        """execute the stored method with the result
            :param func     the method stored
            :param args     actually this almost just refers to `wanted`
        """
        return func(args)

    def run(self, continuous=True, no_output=False):
        """The whole application entry point

        :param continuous   (bool)      continuously execute all the binding methods
                                    then show all the result in the console or execute
                                    and show the result once
                                        if in your method, `print` is deployed more than `return`
                                    well, continuous=False is recommended, but somehow
                                    if you mix them in your method ... the result is not
                                    easy to control, if you can, never mind :)
                                        I just hope there will be most only one kind of display

            The whole process is like:
                1. check the binding list, if None, exit at once
                2. bind the help method, you may not able to set help param manually now
                3. run !

                BUT unfortunately ... the execute order is not decided by the input order, but the order you bind
            the method ... you will notice in the example
                $ seek -t --linux fine
                if actually equal
                $ seek --linux fine -t

                which may be the shortcomings of the package or the example
            if you want to deal with the execute order ... `print` it out and return ''
            for `print` will be execute in your own method and by the INPUT ORDER,
            though ... it's kind of boring, but hope you like it ~~~~
        """

        if not self.collection and not self.no_head_bind:
            print("No binding is detected !!!")
            exit(1)
        self.bind_help()

        result = ''
        no_head = self.no_head_bind
        if no_head and no_head['wanted']:
            result += self.execute(no_head['bind_method'], no_head['wanted'])
            if result:
                self.has_input = True
        # print(self.collection)
        for group in self.collection.values():
            for bind in group:
                if bind['wanted']:
                    self.has_input = True
                    temp_result = self.execute(bind['bind_method'], bind['wanted'])
                    if not continuous and not no_output:
                        print(temp_result)
                    else:
                        result += str(temp_result)
        if result and not no_output:
            print(result)
        if not self.has_input and not no_output:
            print(self.print_help())

