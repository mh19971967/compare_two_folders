import hashlib
import os
import datetime
import blake3


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
            files_dict[file_path[len(def_folder) + 1 :]] = file_path
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

    # files_identical = {}
    # files_only_mtime_difference = {}
    # files_any_difference_but_mtime = {}
    # digits_number_of_files = (
    #     f"0{len(str(min(number_of_files_in_source, number_of_files_in_target)))}d"
    # )
    # time_old = datetime.datetime.now()
    # file_count_old = 0
    # files_to_be_compared = set(files_source.keys()).intersection(
    #     set(files_target.keys())
    # )
    # print(
    #     f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
    #     f"-> Number of files to be compared: '{len(files_to_be_compared)}'"
    # )
    # print("")
    #
    # for idx, file in enumerate(
    #     files_to_be_compared,
    #     1,
    # ):
    #     file_source = files_source[file]
    #     file_target = files_target[file]
    #     results = compare_files(
    #         file_source,
    #         file_target,
    #         def_hash_algorithm,
    #         def_options,
    #     )
    #     if idx % count_tick == 0:
    #         time_new = datetime.datetime.now()
    #         file_count_new = idx
    #         if file_count_new - file_count_old > 0:
    #             number_of_seconds = (time_new - time_old).total_seconds()
    #             number_of_files_compared = file_count_new - file_count_old
    #             comparisons_per_second = number_of_files_compared / number_of_seconds
    #             print_verbose(
    #                 f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
    #                 f"Number of files compared so far: '{file_count_new:{digits_number_of_files}}'",
    #                 def_verbose["general"],
    #             )
    #             print_verbose(
    #                 f"                     -> '{int(round(comparisons_per_second, 0))}' "
    #                 f"comparisons per second ",
    #                 def_verbose["general"],
    #             )
    #             comparison_eta = datetime.timedelta(
    #                 seconds=(minimum_number_of_files - idx) / comparisons_per_second
    #             )
    #             print_verbose(
    #                 f"                     -> ETA: '{comparison_eta}'",
    #                 def_verbose["general"],
    #             )
    #             print_verbose(
    #                 f"                     -> Current file: '{file}'",
    #                 def_verbose["general"],
    #             )
    #             print_verbose(
    #                 "",
    #                 def_verbose["general"],
    #             )
    #         time_old = time_new
    #         file_count_old = file_count_new
    #
    #     # Collect comparison data for files which are identical
    #     if identify_files_identical(results):
    #         files_identical[file] = results
    #
    #     # Collect comparison data for files which are identical but where the modification time maybe different
    #     details_mtime_found = any(
    #         "file_mtime" in test_for_mtime["details"] for test_for_mtime in results
    #     )
    #     if identify_files_only_mtime_difference(results) and details_mtime_found:
    #         files_only_mtime_difference[file] = results
    #
    #     # Collect comparison data for files which are different without considering the modification time
    #     if identify_files_any_difference_but_mtime(results):
    #         files_any_difference_but_mtime[file] = results

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


def compare_folders(
    def_folder_source,
    def_folder_target,
    def_hash_algorithm,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose=None,
):
    def print_files_identical(def_files_identical):
        digits_pass = f"0{len(str(len(def_files_identical)))}d"
        count_files = 0
        for idx, file in enumerate(
            def_files_identical,
            1,
        ):
            count_files += 1
            print_verbose(
                f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                f"PASS:      Files are identical:    '{file}' (file number: '{idx:{digits_pass}}')",
                def_verbose["files-pass"],
            )
            for detail in def_files_identical[file]:
                print_verbose(
                    f"                     -> {detail}",
                    def_verbose["files-pass"],
                )
        if def_files_identical:
            print()
        return count_files

    def print_files_missing(
        def_files,
        def_info_text,
    ):
        count_files = 0
        for idx, (file, path) in enumerate(
            def_files.items(),
            1,
        ):
            count_files += 1
            print(
                f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                f"{def_info_text}: '{file}' in '{def_folder_source}'"
            )
        if def_files.items():
            print()
        return count_files

    def print_files_only_mtime_difference(def_files_only_mtime_difference):
        count_files = 0
        for idx, (file, details) in enumerate(
            def_files_only_mtime_difference.items(),
            1,
        ):
            count_files += 1
            print(
                f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                f"ERROR->OK: File differs:           '{file}':"
            )
            print(
                "                     -> OK: Only mtime differs. "
                "Files are otherwise identical (size, hash or bits)."
            )
            for detail in details:
                print(f"                     -> {detail}")
        if def_files_only_mtime_difference:
            print()
        return count_files

    def print_files_any_difference_but_mtime(def_files_any_difference_but_mtime):
        count_files = 0
        for idx, (file, details) in enumerate(
            def_files_any_difference_but_mtime.items(),
            1,
        ):
            count_files += 1
            print(
                f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                f"ERROR1:     File differs:           '{file}':"
            )
            for detail in details:
                print(f"                     -> {detail}")
        if def_files_any_difference_but_mtime:
            print()
        return count_files

    if not os.path.exists(def_folder_source):
        print(f"ERROR: Source folder '{def_folder_source}' does not exist")
        exit()
    if not os.path.exists(def_folder_target):
        print(f"ERROR: Target folder '{def_folder_target}' does not exist")
        exit()

    if def_verbose is None:
        def_verbose = {
            "general": True,
            "files-pass": True,
            "summary": True,
        }
    (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
        files_source_size,
        files_target_size,
    ) = evaluate_file_comparison_state(
        def_folder_source,
        def_folder_target,
        def_hash_algorithm,
        def_exclude_files,
        def_exclude_extensions,
        def_options,
        def_verbose,
    )

    print()
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Evaluation of files comparison"
    )
    print_verbose(
        "",
        def_verbose["general"],
    )

    # Printing all identical files
    count_files_pass = print_files_identical(files_identical)

    # Printing all files missing in source
    count_files_missing_in_source = print_files_missing(
        files_missing_source,
        "WARNING:   File missing in source",
    )
    # TODO: COPY TO TARGET?

    # Printing all files missing in target
    count_files_missing_in_target = print_files_missing(
        files_missing_target,
        "ERROR:     File missing in target",
    )

    # Printing all files which are identical apart from the modification times (mtime)
    count_files_only_mtime_difference = print_files_only_mtime_difference(
        files_only_mtime_difference
    )

    # Printing all files which are identical apart from the modification times (mtime)
    count_files_any_difference_but_mtime = print_files_any_difference_but_mtime(
        files_any_difference_but_mtime
    )

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Evaluation of files comparison"
    )
    print()
    print()
    return {
        "files_pass": count_files_pass,
        "files_missing_in_source": count_files_missing_in_source,
        "files_missing_in_target": count_files_missing_in_target,
        "files_only_mtime_difference": count_files_only_mtime_difference,
        "files_any_difference_but_mtime": count_files_any_difference_but_mtime,
        "files_source_size": files_source_size,
        "files_target_size": files_target_size,
    }


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    # if len(sys.argv) != 3:
    #     print("Usage: python compare_folders.py folder1 folder2")
    #     sys.exit(1)
    # folder1 = sys.argv[1]
    # folder2 = sys.argv[2]

    # /usr/local/bin/rsync -avzHXA --delete --progress --progress --stats --dry-run --iconv=UTF8,UTF8-MAC
    # --checksum test1/ test2/

    folder1 = "/Users/mh/temp/test1"
    folder2 = "/Users/mh/temp/test2"
    # folder1 = "/Users/mh/temp/movieposters1"
    # folder2 = "/Users/mh/temp/movieposters2"
    # folder1 = "/Users/mh/temp/01 - Januar"
    # folder2 = "/Users/mh/temp/02 - Januar"
    # folder1 = "/Volumes/Untitled"
    # folder2 = "/Users/mh/Documents/DJI Mini 3 Pro/DJI Mini 3 Pro"

    # Optional: specify a list of files to exclude
    # exclude_files = [".DS_Store"]
    exclude_files = []

    # Optional: specify a list of file extensions to exclude
    # exclude_extensions = [".log"]
    exclude_extensions = []

    options_all_possible = [
        "S",
        "T",
        "H",
        "B",
        "ST",
        "SH",
        "SB",
        "TH",
        "TB",
        "HB",
        "STH",
        "STB",
        "SHB",
        "THB",
        "STHB",
    ]

    options = ["STHB"]
    # S = Compare the files for their size
    # T = Compare the files for their modification time
    # H = Compare the files using hashes
    # B = Compare the files bitwise

    verbose = {
        "general": True,
        "files-pass": True,
        "summary": True,
    }

    hash_algorithm = "blake3"
    # Possible algorithms:
    # "sha256"
    # "sha3_256"
    # "blake2s" (256-bit)
    # "sha512"
    # "sha3_512"
    # "blake2b" (512-bit)
    # "blake3" (512-bit)

    for option in options:
        return_data = compare_folders(
            folder1,
            folder2,
            hash_algorithm,
            exclude_files,
            exclude_extensions,
            option,
            verbose,
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"SUMMARY:",
            verbose["summary"],
        )
        number_files_pass = return_data["files_pass"]
        number_files_missing_in_source = return_data["files_missing_in_source"]
        number_files_missing_in_target = return_data["files_missing_in_target"]
        number_files_only_mtime_difference = return_data["files_only_mtime_difference"]
        number_files_any_difference_but_mtime = return_data[
            "files_any_difference_but_mtime"
        ]
        number_files_source_size = return_data["files_source_size"]
        number_files_target_size = return_data["files_target_size"]
        sum_both = (
            number_files_pass
            + number_files_only_mtime_difference
            + number_files_any_difference_but_mtime
        )
        sum_source = sum_both + number_files_missing_in_target
        sum_target = sum_both + number_files_missing_in_source
        digits_num_files = f"0{len(str(max(sum_source, sum_target)))}d"
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files passed as being identical:                "
            f"'{number_files_pass:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files missing in source:                        "
            f"'{number_files_missing_in_source:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files missing in target:                        "
            f"'{number_files_missing_in_target:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files where only mtime differs:                 "
            f"'{number_files_only_mtime_difference:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files where something differs other than mtime: "
            f"'{number_files_any_difference_but_mtime:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            "",
            verbose["summary"],
        )

        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files in source:                                "
            f"'{sum_source:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files in target:                                "
            f"'{sum_target:{digits_num_files}}'",
            verbose["summary"],
        )
        print_verbose(
            "",
            verbose["summary"],
        )

        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Total size of files in source:                            "
            f"'{number_files_source_size}' bytes",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Total size of files in target:                            "
            f"'{number_files_target_size}' bytes",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Delta:                                                    "
            f"'{abs(number_files_target_size - number_files_source_size)}' bytes",
            verbose["summary"],
        )
        print_verbose(
            "",
            verbose["summary"],
        )

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Running time: "
            f"'{elapsed_time}'",
            verbose["summary"],
        )
