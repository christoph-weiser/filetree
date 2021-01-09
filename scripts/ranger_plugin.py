class dircomp(Command):
    """:dircomp [-FLAGS...]

    Compare the content of two paths, provided by two open tabs
    that will be compared.

    Flags:
     -s: compare directory structure.
     -b: compare two file and folder wise identical structures for binary differences.
     -p: output the result to the pager.
     -e: output the result to file and open with editor in new tab.
    """

    def __init__(self, *args, **kwargs):
        super(dircomp, self).__init__(*args, **kwargs)
        self.flags, _ = self.parse_flags()

    def execute(self):
        import ranger.ext.filetree as ft
        from os.path import expanduser
        ft_a = ft.Filetree(str(self.fm.tabs[1].thisdir))
        ft_b = ft.Filetree(str(self.fm.tabs[2].thisdir))

        data_list = []

        # count, set or bin comparison switch.
        if "b" in self.flags:
            res = ft_a.compare(ft_b, "binary")
            if res.result:
                data_list.append(">>> Same Binary content.")
            else:
                data_list.append(">>> Binary difference in:")
                for elem in res.diff:
                    data_list.append(str(elem))
            data_output = "\n".join(data_list)
        else:
            res = ft_a.compare(ft_b, "set")
            data_list.append(">>> Missing in tab 1")
            for elem in res.missing_a:
                data_list.append(str(elem))
            data_list.append(">>> Missing in tab 2")
            for elem in res.missing_b:
                data_list.append(str(elem))
            data_output = "\n".join(data_list)

        output_dir = expanduser("~") + "/.cache/ranger/"
        output_filename = "diff.txt"

        # pager or editor output switch.
        if "e" in self.flags:
            with open((output_dir + output_filename), "w") as diff_file:
                diff_file.write(data_output)
            self.fm.tab_switch(output_dir)
            self.fm.edit_file(output_filename)
        else:
            pager = self.fm.ui.open_pager()
            pager.set_source(data_output)
