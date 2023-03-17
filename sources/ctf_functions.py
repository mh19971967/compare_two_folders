import hashlib
import blake3
import os
import datetime

# Module "string": Common string operations
# (https://docs.python.org/3.11/library/sys.html#module-sys)
from string import Template


class DeltaTemplate(Template):
    """
    String template for timedelta objects formatted strings
    """

    delimiter = "%"


def strfdelta(
    def_time_delta,
    def_time_delta_format,
):
    """
    Generates the string for a timedelta object.
    :param def_time_delta:        timedelta, timedelta object
    :param def_time_delta_format:       str, format of the timedelta object string
    :return:                            str, timedelta formatted string
    """
    d = {"D": def_time_delta.days}
    hours, rem = divmod(
        def_time_delta.seconds,
        3600,
    )
    minutes, seconds = divmod(
        rem,
        60,
    )
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(def_time_delta_format)
    return t.substitute(**d)


def get_file_hash(def_file_path):
    with open(def_file_path, "rb") as f:
        file_data = f.read()
        return hashlib.sha512(file_data).hexdigest()


def sha_hash(
    def_filename,
    def_hash_algorithm,
):
    """Calculate the SHA512 hash of a file."""
    if def_hash_algorithm == "sha256":
        sha = hashlib.sha256()
    elif def_hash_algorithm == "sha3_256":
        sha = hashlib.sha3_256()
    elif def_hash_algorithm == "blake2s":
        sha = hashlib.blake2s()
    elif def_hash_algorithm == "sha512":
        sha = hashlib.sha512()
    elif def_hash_algorithm == "sha3_512":
        sha = hashlib.sha3_512()
    elif def_hash_algorithm == "blake2b":
        sha = hashlib.blake2b()
    elif def_hash_algorithm == "blake3":
        sha = blake3.blake3()
    else:
        raise NotImplementedError(f"No hash algorithm: '{def_hash_algorithm}'")
    with open(def_filename, "rb") as f:
        while True:
            if data := f.read(4096):
                sha.update(data)
            else:
                break
    return sha.hexdigest()


def print_verbose(
    def_message,
    def_verbose,
):
    if def_verbose:
        print(def_message)


def search_file(filename, search_path="."):
    """
    Search for a file in a folder and its sub folders recursively.
    """
    # Iterate through all files and sub folders in the search path
    for root, dirnames, filenames in os.walk(search_path):
        # Check if the file is in the current directory
        if filename in filenames:
            return os.path.join(root, filename)
    # File not found
    return None

def compare_files(
    def_file_source,
    def_file_target,
    def_hash_algorithm,
    def_options,
):
    # Get file status
    file_source_stat = os.stat(def_file_source)
    file_target_stat = os.stat(def_file_target)

    # Check file size
    file_size = None
    if "S" in def_options:
        file_source_size = file_source_stat.st_size
        file_target_size = file_target_stat.st_size
        file_size = {
            "details": "file_size",
            "result": file_source_stat.st_size == file_target_stat.st_size,
            "file_source_data": str(file_source_size),
            "file_target_data": str(file_target_size),
        }

    # Check modification time
    file_mtime = None
    if "T" in def_options:
        file_mtime = {
            "details": "file_mtime",
            "result": file_source_stat.st_mtime == file_target_stat.st_mtime,
            "file_source_data": str(
                datetime.datetime.fromtimestamp(file_source_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            "file_target_data": str(
                datetime.datetime.fromtimestamp(file_target_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
        }

    # Check file hash
    file_hash = None
    if "H" in def_options:
        file_source_hash = sha_hash(
            def_file_source,
            def_hash_algorithm=def_hash_algorithm,
        )
        file_target_hash = sha_hash(
            def_file_target,
            def_hash_algorithm=def_hash_algorithm,
        )
        file_hash = {
            "details": "file_hash",
            "result": file_source_hash == file_target_hash,
            "file_source_data": str(file_source_hash),
            "file_target_data": str(file_target_hash),
        }

    # Check bitwise comparison
    file_bit = None
    if "B" in def_options:
        file_bit = {
            "details": "file_bit",
            "result": True,
            "file_source_data": "",
            "file_target_data": "",
        }
        with open(def_file_source, "rb") as f1, open(def_file_target, "rb") as f2:
            for b1, b2 in zip(
                iter(lambda: f1.read(4096), b""),
                iter(lambda: f2.read(4096), b""),
            ):
                if b1 != b2:
                    file_bit["result"] = False
                    break

    results = []
    if file_size is not None:
        results.append(file_size)
    if file_mtime is not None:
        results.append(file_mtime)
    if file_hash is not None:
        results.append(file_hash)
    if file_bit is not None:
        results.append(file_bit)
    return results

def create_file_dict(
    def_folder,
    def_exclude_files=None,
    def_exclude_extensions=None,
):
    files_dict = {}
    file_size = 0
    for root, dirs, files in os.walk(
        def_folder,
        topdown=False,
    ):
        for file in files:
            # Skip excluded files
            if def_exclude_files and file in def_exclude_files:
                continue
            # Skip excluded file extensions
            if (
                def_exclude_extensions
                and os.path.splitext(file)[1].lower() in def_exclude_extensions
            ):
                continue
            file_path = os.path.join(root, file)
            number_of_characters_def_folder = len(def_folder) + 1
            files_dict[file_path[number_of_characters_def_folder:]] = file_path
            file_size += os.stat(file_path).st_size
    return files_dict, file_size


def identify_files_identical(def_results):
    return all((item["result"] for item in def_results))


def identify_files_only_mtime_difference(def_results):
    return not any(
        (item["details"] != "file_mtime" and not item["result"])
        or (item["details"] == "file_mtime" and item["result"])
        for item in def_results
    )


def identify_files_any_difference_but_mtime(def_results):
    return any(
        item["details"] != "file_mtime" and not item["result"] for item in def_results
    )


def print_initial_information(
    def_options,
    def_hash_algorithm,
    def_folder_source,
    def_folder_target,
    def_number_of_files_in_source,
    def_number_of_files_in_target,
    def_files_source_size,
    def_files_target_size,
):
    print()
    print(">>>>>>>>> Comparing two folders <<<<<<<<<")
    print()
    print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"OPTIONS:  '{def_options}' is requested"
    )
    if "S" in def_options:
        print("                     -> S: Comparing the files for their size")
    if "T" in def_options:
        print(
            "                     -> T: Comparing the files for their modification time"
        )
    if "H" in def_options:
        print(
            f"                     -> H: Comparing the files for their hashes (algorithm: '{def_hash_algorithm}')"
        )
    if "B" in def_options:
        print("                     -> B: Comparing the files bitwise")

    print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"SOURCE:   '{def_folder_source}' (number of files in source: '{def_number_of_files_in_source}')"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TARGET:   '{def_folder_target}' (number of files in target: '{def_number_of_files_in_target}')"
    )
    print()

    if def_number_of_files_in_source != def_number_of_files_in_target:
        delta = abs(def_number_of_files_in_source - def_number_of_files_in_target)
        files_count = "file" if delta == 1 else "files"
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   Number of files in source and target are different\n"
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"DELTA:     -> '{delta}' {files_count}"
        )
        print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"SOURCE:   Total size of files: '{def_files_source_size}' bytes"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TARGET:   Total size of files: '{def_files_target_size}' bytes"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"DELTA:    "
        f"'{abs(def_files_target_size - def_files_source_size)}' bytes"
    )
    print()


def collect_comparison_data(
    def_number_of_files_in_source,
    def_number_of_files_in_target,
    def_files_source,
    def_files_target,
    def_hash_algorithm,
    def_options,
    def_count_tick,
    def_verbose,
    def_minimum_number_of_files,
):
    files_identical = {}
    files_only_mtime_difference = {}
    files_any_difference_but_mtime = {}
    digits_number_of_files = f"0{len(str(min(def_number_of_files_in_source, def_number_of_files_in_target)))}d"
    time_old = datetime.datetime.now()
    file_count_old = 0
    files_to_be_compared = set(def_files_source.keys()).intersection(
        set(def_files_target.keys())
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"-> Number of files to be compared: '{len(files_to_be_compared)}'"
    )
    print("")

    for idx, file in enumerate(
        files_to_be_compared,
        1,
    ):
        file_source = def_files_source[file]
        file_target = def_files_target[file]
        results = compare_files(
            file_source,
            file_target,
            def_hash_algorithm,
            def_options,
        )
        if idx % def_count_tick == 0:
            time_new = datetime.datetime.now()
            file_count_new = idx
            if file_count_new - file_count_old > 0:
                number_of_seconds = (time_new - time_old).total_seconds()
                number_of_files_compared = file_count_new - file_count_old
                comparisons_per_second = number_of_files_compared / number_of_seconds
                print_verbose(
                    f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                    f"Number of files compared so far: '{file_count_new:{digits_number_of_files}}'",
                    def_verbose["general"],
                )
                print_verbose(
                    f"                     -> '{int(round(comparisons_per_second, 0))}' "
                    f"comparisons per second ",
                    def_verbose["general"],
                )
                comparison_eta = datetime.timedelta(
                    seconds=(def_minimum_number_of_files - idx) / comparisons_per_second
                )
                print_verbose(
                    f"                     -> ETA: '{comparison_eta}'",
                    def_verbose["general"],
                )
                print_verbose(
                    f"                     -> Current file: '{file}'",
                    def_verbose["general"],
                )
                print_verbose(
                    "",
                    def_verbose["general"],
                )
            time_old = time_new
            file_count_old = file_count_new

        # Collect comparison data for files which are identical
        if identify_files_identical(results):
            files_identical[file] = results

        # Collect comparison data for files which are identical but where the modification time maybe different
        details_mtime_found = any(
            "file_mtime" in test_for_mtime["details"] for test_for_mtime in results
        )
        if identify_files_only_mtime_difference(results) and details_mtime_found:
            files_only_mtime_difference[file] = results

        # Collect comparison data for files which are different without considering the modification time
        if identify_files_any_difference_but_mtime(results):
            files_any_difference_but_mtime[file] = results

    return files_identical, files_only_mtime_difference, files_any_difference_but_mtime


def evaluate_file_comparison_state(
    def_folder_source,
    def_folder_target,
    def_hash_algorithm,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose=None,
):
    if def_verbose is None:
        def_verbose = {
            "general": True,
            "files-pass": True,
            "summary": True,
        }

    # Store the files in each folder
    files_source, files_source_size = create_file_dict(
        def_folder_source,
        def_exclude_files,
        def_exclude_extensions,
    )
    files_target, files_target_size = create_file_dict(
        def_folder_target,
        def_exclude_files,
        def_exclude_extensions,
    )

    number_of_files_in_source = len(files_source)
    number_of_files_in_target = len(files_target)

    print_initial_information(
        def_options,
        def_hash_algorithm,
        def_folder_source,
        def_folder_target,
        number_of_files_in_source,
        number_of_files_in_target,
        files_source_size,
        files_target_size,
    )

    minimum_number_of_files = min(
        number_of_files_in_source,
        number_of_files_in_target,
    )
    maximum_number_of_files = max(
        number_of_files_in_source,
        number_of_files_in_target,
    )

    count_tick = round(
        0.1 * maximum_number_of_files,
        0,
    )

    # Check for missing files in source and target
    missing_files_source = set(files_source.keys()).difference(set(files_target.keys()))
    missing_files_target = set(files_target.keys()).difference(set(files_source.keys()))
    files_missing_target = {
        missing_file_target: f"{def_folder_target}/{missing_file_target}"
        for missing_file_target in missing_files_source
    }
    files_missing_source = {
        missing_file_source: f"{def_folder_target}/{missing_file_source}"
        for missing_file_source in missing_files_target
    }

    # Compare files
    comparison_start_time = datetime.datetime.now()
    print("")
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Comparison of files"
    )

    (
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
    ) = collect_comparison_data(
        number_of_files_in_source,
        number_of_files_in_target,
        files_source,
        files_target,
        def_hash_algorithm,
        def_options,
        count_tick,
        def_verbose,
        minimum_number_of_files,
    )

    comparison_end_time = datetime.datetime.now()
    elapsed_compare_time = comparison_end_time - comparison_start_time

    elapsed_run_time_format: str = "%H:%M:%S"
    elapsed_run_time_string = strfdelta(elapsed_compare_time, elapsed_run_time_format)
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TIME:      '{elapsed_run_time_string}'\n"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Comparison of files"
    )
    print()

    return (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
        files_source_size,
        files_target_size,
    )
