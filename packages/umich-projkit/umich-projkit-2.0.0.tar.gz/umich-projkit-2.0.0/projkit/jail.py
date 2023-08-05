class Jail(object):
    """Simulates the autograder jail."""
    def __init__(self, directory, time_limit, disk_limit, memory_limit):
        """Constructor."""
        self.directory = directory
        self.time_limit = time_limit
        self.disk_limit = disk_limit
        self.memory_limit = memory_limit

    def run(
        self,
        command,
        accept_failure=False,
        limited=False
    ):
        """Runs the given command in the jail, without limiting resources. It's
        assumed that the script has pre-sanitized the command.

        """
        if limited:
            command = (
                "ulimit -f {disk} && "
                "ulimit -t {time} && "
                "ulimit -m {memory} && "
                "{command}".format(
                    disk=self.disk_limit,
                    time=self.time_limit,
                    memory=self.memory_limit,
                    command=command
                )
            )

        logging.info("Running command '{command}'".format(command=command))
        return_code = subprocess.call(command, shell=True)

        if return_code != 0 and not accept_failure:
            die("Command failed: '{command}'".format(command=command))

        return return_code

    @contextlib.contextmanager
    def cd(self, new_dir):
        old_dir = os.getcwd()
        try:
            os.chdir(new_dir)
            yield
        finally:
            os.chdir(old_dir)


@contextlib.contextmanager
def make_jail(time_limit, disk_limit, memory_limit):
    """Construct a new jail, which will be cleaned up afterward."""
    jail_dir = tempfile.mkdtemp()
    logging.info("Jail dir is {jail_dir}".format(jail_dir=jail_dir))
    jail = Jail(jail_dir, time_limit, disk_limit, memory_limit)
    try:
        with jail.cd(jail_dir):
            yield jail
    finally:
        shutil.rmtree(jail_dir)


