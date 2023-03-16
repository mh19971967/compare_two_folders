import hashlib
import os
import datetime
import blake3


# Module "string": Common string operations
# (https://docs.python.org/3.11/library/sys.html#module-sys)
from string import Template


class DeltaTemplate(
    Template,
):
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


def sha_hash(def_filename, def_hash_algorithm="sha3_256"):
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
    def_file1,
    def_file2,
    def_options,
    def_hash_algorithm,
):
    # Get file status
    file1_stat = os.stat(def_file1)
    file2_stat = os.stat(def_file2)

    # Check file size
    file_size = None
    if "S" in def_options:
        file1_size = file1_stat.st_size
        file2_size = file2_stat.st_size
        file_size = {
            "details": "file_size",
            "result": file1_stat.st_size == file2_stat.st_size,
            "file1_data": str(file1_size),
            "file2_data": str(file2_size),
        }

    # Check modification time
    file_mtime = None
    if "T" in def_options:
        file_mtime = {
            "details": "file_mtime",
            "result": file1_stat.st_mtime == file2_stat.st_mtime,
            "file1_data": str(
                datetime.datetime.fromtimestamp(file1_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            "file2_data": str(
                datetime.datetime.fromtimestamp(file2_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
        }

    # Check file hash
    file_hash = None
    if "H" in def_options:
        file1_hash = sha_hash(def_file1, def_hash_algorithm=def_hash_algorithm)
        file2_hash = sha_hash(def_file2, def_hash_algorithm=def_hash_algorithm)
        file_hash = {
            "details": "file_hash",
            "result": file1_hash == file2_hash,
            "file1_data": str(file1_hash),
            "file2_data": str(file2_hash),
        }

    # Check bitwise comparison
    file_bit = None
    if "B" in def_options:
        file_bit = {
            "details": "file_bit",
            "result": True,
            "file1_data": "",
            "file2_data": "",
        }
        with open(def_file1, "rb") as f1, open(def_file2, "rb") as f2:
            for b1, b2 in zip(
                iter(lambda: f1.read(4096), b""), iter(lambda: f2.read(4096), b"")
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
    for root, dirs, files in os.walk(def_folder, topdown=False):
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


def evaluate_file_comparison_state(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose=None,
    def_hash_algorithm="sha3_512",
):
    if def_verbose is None:
        def_verbose = {
            "general": True,
            "files-pass": True,
        }

    # Store the files in each folder
    files1, files1_size = create_file_dict(
        def_folder1,
        def_exclude_files,
        def_exclude_extensions,
    )
    files2, files2_size = create_file_dict(
        def_folder2,
        def_exclude_files,
        def_exclude_extensions,
    )

    number_of_files_in_source = len(files1)
    number_of_files_in_target = len(files2)

    minimum_number_of_files = min(number_of_files_in_source, number_of_files_in_target)

    count_tick = round(
        0.1 * max(number_of_files_in_source, number_of_files_in_target), 0
    )

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
        f"SOURCE:   '{def_folder1}' (number of files in source: '{number_of_files_in_source}')"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TARGET:   '{def_folder2}' (number of files in target: '{number_of_files_in_target}')"
    )
    print()

    if number_of_files_in_source != number_of_files_in_target:
        delta = abs(number_of_files_in_source - number_of_files_in_target)
        files_count = "files"
        if delta == 1:
            files_count = "file"
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   Number of files in source and target are different\n"
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"DELTA:     -> '{delta}' {files_count}"
        )
        print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"SOURCE:   Total size of files: '{files1_size}' bytes"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TARGET:   Total size of files: '{files2_size}' bytes"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"DELTA:    "
        f"'{abs(files2_size - files1_size)}' bytes"
    )
    print()

    # Check for missing files
    missing_files1 = set(files1.keys()).difference(set(files2.keys()))
    missing_files2 = set(files2.keys()).difference(set(files1.keys()))
    files_missing_target = {
        missing_file_target: f"{def_folder2}/{missing_file_target}"
        for missing_file_target in missing_files1
    }
    files_missing_source = {
        missing_file_source: f"{def_folder2}/{missing_file_source}"
        for missing_file_source in missing_files2
    }

    # Compare files
    comparison_start_time = datetime.datetime.now()
    print("")
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Comparison of files"
    )

    files_identical = {}
    files_only_mtime_difference = {}
    files_any_difference_but_mtime = {}
    digits_number_of_files = (
        f"0{len(str(min(number_of_files_in_source, number_of_files_in_target)))}d"
    )
    time_old = datetime.datetime.now()
    file_count_old = 0
    files_to_be_compared = set(files1.keys()).intersection(set(files2.keys()))
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"-> Number of files to be compared: '{len(files_to_be_compared)}'"
    )
    print("")
    for idx, file in enumerate(files_to_be_compared, 1):
        file1 = files1[file]
        file2 = files2[file]
        results = compare_files(
            file1,
            file2,
            def_options,
            def_hash_algorithm,
        )
        if idx % count_tick == 0:
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
                    seconds=(minimum_number_of_files - idx) / comparisons_per_second
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

        def check_files_identical(def_results):
            return all((item["result"] for item in def_results))

        if check_files_identical(results):
            files_identical[file] = results

        def check_files_any_difference_but_mtime(def_results):
            for item in def_results:
                if item["details"] != "file_mtime" and not item["result"]:
                    return True
            return False

        if check_files_any_difference_but_mtime(results):
            files_any_difference_but_mtime[file] = results

        def check_files_only_mtime_difference(def_results):
            for item in def_results:
                if item["details"] != "file_mtime" and not item["result"]:
                    return False
                if item["details"] == "file_mtime" and item["result"]:
                    return False
            return True

        details_mtime_found = False
        for test_for_mtime in results:
            if "file_mtime" in test_for_mtime["details"]:
                details_mtime_found = True

        if check_files_only_mtime_difference(results) and details_mtime_found:
            files_only_mtime_difference[file] = results

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
        files1_size,
        files2_size,
    )


def compare_folders(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose=None,
    def_hash_algorithm="sha3_512",
):
    if def_verbose is None:
        def_verbose = {
            "general": True,
            "files-pass": True,
        }
    (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
        files1_size,
        files2_size,
    ) = evaluate_file_comparison_state(
        def_folder1,
        def_folder2,
        def_exclude_files,
        def_exclude_extensions,
        def_options,
        def_verbose,
        def_hash_algorithm,
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

    digits_pass = f"0{len(str(len(files_identical)))}d"
    count_files_pass = 0
    for idx, file in enumerate(files_identical, 1):
        count_files_pass += 1
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"PASS:      Files are identical:    '{file}' (file number: '{idx:{digits_pass}}')",
            def_verbose["files-pass"],
        )
        for detail in files_identical[file]:
            print_verbose(
                f"                     -> {detail}",
                def_verbose["files-pass"],
            )

    if files_identical:
        print()

    count_files_missing_in_source = 0
    for idx, (file, path) in enumerate(files_missing_source.items(), 1):
        count_files_missing_in_source += 1
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   File missing in source: '{file}' in '{def_folder1}'"
        )
    if files_missing_source.items():
        print()

    count_files_missing_in_target = 0
    for idx, (file, path) in enumerate(files_missing_target.items(), 1):
        count_files_missing_in_target += 1
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File missing in target: '{file}' in '{def_folder2}'"
        )
        # TODO: COPY TO TARGET?
    if files_missing_target.items():
        print()

    count_files_only_mtime_difference = 0
    for idx, (file, details) in enumerate(files_only_mtime_difference.items(), 1):
        count_files_only_mtime_difference += 1
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
    if files_only_mtime_difference:
        print()

    count_files_any_difference_but_mtime = 0
    for idx, (file, details) in enumerate(files_any_difference_but_mtime.items(), 1):
        count_files_any_difference_but_mtime += 1
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File differs:           '{file}':"
        )
        for detail in details:
            print(f"                     -> {detail}")
    if files_any_difference_but_mtime:
        print()

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
        "files1_size": files1_size,
        "files2_size": files2_size,
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
            exclude_files,
            exclude_extensions,
            option,
            verbose,
            hash_algorithm,
        )
        print_verbose(f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                      f"SUMMARY:", verbose["summary"])
        number_files_pass = return_data["files_pass"]
        number_files_missing_in_source = return_data["files_missing_in_source"]
        number_files_missing_in_target = return_data["files_missing_in_target"]
        number_files_only_mtime_difference = return_data["files_only_mtime_difference"]
        number_files_any_difference_but_mtime = return_data[
            "files_any_difference_but_mtime"
        ]
        number_files1_size = return_data["files1_size"]
        number_files2_size = return_data["files2_size"]
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
            f"'{number_files1_size}' bytes",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Total size of files in target:                            "
            f"'{number_files2_size}' bytes",
            verbose["summary"],
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Delta:                                                    "
            f"'{abs(number_files2_size - number_files1_size)}' bytes",
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
