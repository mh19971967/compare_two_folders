import hashlib
import os
import datetime

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


def sha512_hash(def_filename):
    """Calculate the SHA512 hash of a file."""
    sha512 = hashlib.sha512()
    with open(def_filename, "rb") as f:
        while True:
            if data := f.read(4096):
                sha512.update(data)
            else:
                break
    return sha512.hexdigest()


def compare_files(
    def_file1,
    def_file2,
):
    options = "STHB"
    # Get file status
    file1_stat = os.stat(def_file1)
    file2_stat = os.stat(def_file2)

    # Check file size
    file1_size = file1_stat.st_size
    file2_size = file2_stat.st_size
    file_size = {
        "result": file1_stat.st_size == file2_stat.st_size if "S" in options else None,
        "file1_data": str(file1_size) if "S" in options else "",
        "file2_data": str(file2_size) if "S" in options else "",
    }

    # Check modification time
    file_mtime = {
        "result": file1_stat.st_mtime == file2_stat.st_mtime
        if "T" in options
        else None,
        "file1_data": str(
            datetime.datetime.fromtimestamp(file1_stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        if "T" in options
        else "",
        "file2_data": str(
            datetime.datetime.fromtimestamp(file2_stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        if "T" in options
        else "",
    }

    # Check file hash
    file1_hash = sha512_hash(def_file1)
    file2_hash = sha512_hash(def_file2)
    file_hash = {
        "result": file1_hash == file2_hash if "H" in options else None,
        "file1_data": str(file1_hash) if "H" in options else "",
        "file2_data": str(file2_hash) if "H" in options else "",
    }

    # Check bitwise comparison
    file_bit = {
        "result": True if "B" in options else None,
        "file1_data": "",
        "file2_data": "",
    }
    with open(def_file1, "rb") as f1, open(def_file2, "rb") as f2:
        while True:
            b1 = f1.read(4096)
            b2 = f2.read(4096)
            if b1 != b2:
                file_bit["result"] = False if "B" in options else None
            if not b1:
                break

    return file_size, file_mtime, file_hash, file_bit


def create_file_dict(
    def_folder,
    def_exclude_files=None,
    def_exclude_extensions=None,
):
    files_dict = {}
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
    return files_dict


def evaluate_file_comparison_state(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
):
    # Store the files in each folder
    files1 = create_file_dict(
        def_folder1,
        def_exclude_files,
        def_exclude_extensions,
    )
    files2 = create_file_dict(
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
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   Number of files in source and target are different\n"
            f"DELTA:     -> {abs(number_of_files_in_target - number_of_files_in_source)} files"
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
    print()
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Comparison"
    )
    print()

    files_identical = {}
    files_only_mtime_difference = {}
    files_any_difference_but_mtime = {}
    digits = f"0{len(str(min(number_of_files_in_source, number_of_files_in_target)))}d"
    time_old = datetime.datetime.now()
    file_count_old = 0
    for idx, file in enumerate(set(files1.keys()).intersection(set(files2.keys()))):
        file1 = files1[file]
        file2 = files2[file]
        file_size, file_mtime, file_hash, file_bit = compare_files(file1, file2)
        if idx % count_tick == 0:
            time_new = datetime.datetime.now()
            file_count_new = idx
            if file_count_new - file_count_old > 0:
                number_of_seconds = (time_new - time_old).total_seconds()
                number_of_files_compared = file_count_new - file_count_old
                comparisons_per_second = number_of_files_compared / number_of_seconds
                print(
                    f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                    f"Number of files compared so far: {file_count_new + 1:{digits}}"
                )
                print(
                    f"                     -> {int(round(comparisons_per_second, 0))} "
                    f"comparisons per second "
                )
                comparison_eta = (
                    minimum_number_of_files - idx
                ) / comparisons_per_second
                print(f"                     -> ETA = {round(comparison_eta, 1)}")
                print(f"                     -> Current file: '{file}'")
                print()
            time_old = time_new
            file_count_old = file_count_new

        if (
            file_mtime["result"]
            and file_size["result"]
            and file_hash["result"]
            and file_bit["result"]
        ):
            files_identical[file] = {
                "file_size": file_size,
                "file_mtime": file_mtime,
                "file_hash": file_hash,
                "file_bit": file_bit,
            }
        elif (
            not file_size["result"] or not file_hash["result"] or not file_bit["result"]
        ):
            files_any_difference_but_mtime[file] = {
                "file_size": file_size,
                "file_mtime": file_mtime,
                "file_hash": file_hash,
                "file_bit": file_bit,
            }
        else:
            files_only_mtime_difference[file] = {
                "file_size": file_size,
                "file_mtime": file_mtime,
                "file_hash": file_hash,
                "file_bit": file_bit,
            }
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Comparison"
    )
    comparison_end_time = datetime.datetime.now()
    elapsed_compare_time = comparison_end_time - comparison_start_time

    elapsed_run_time_format: str = "%H:%M:%S"
    elapsed_run_time_string = strfdelta(elapsed_compare_time, elapsed_run_time_format)
    print(f"                     -> ELAPSED TIME: {elapsed_run_time_string}")
    print()

    return (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
    )


def compare_folders(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
):
    (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
    ) = evaluate_file_comparison_state(
        def_folder1,
        def_folder2,
        def_exclude_files,
        def_exclude_extensions,
    )

    print()
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Evaluation of comparison"
    )

    digits = f"0{len(str(len(files_identical)))}d"
    for idx, file in enumerate(files_identical):
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"PASS:      Files are identical:    '{file}' (file number: {idx + 1:{digits}})."
        )

    print()
    for file, path in files_missing_source.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   File missing in source: '{file}' in '{def_folder1}'."
        )

    print()
    for file, path in files_missing_target.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File missing in target: '{file}' in '{def_folder2}'."
        )
        # TODO: COPY TO TARGET?

    print()
    for file, details in files_only_mtime_difference.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR->OK: File differs:           '{file}'."
        )
        print(
            "                     -> OK: Only mtime differs. "
            "Files are otherwise identical (size, hash, bits)."
        )
        for cause, detail in details.items():
            print(f"                     -> Details: {cause}: {detail}")

    print()
    for file, details in files_any_difference_but_mtime.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File differs:           '{file}'."
        )
        for cause, detail in details.items():
            print(f"                     -> Details: {cause}: {detail}")

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Evaluation of comparison"
    )


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python compare_folders.py folder1 folder2")
    #     sys.exit(1)
    # folder1 = sys.argv[1]
    # folder2 = sys.argv[2]

    # /usr/local/bin/rsync -avzHXA --delete --progress --progress --stats --dry-run --iconv=UTF8,UTF8-MAC --checksum test1/ test2/

    folder1 = "/Users/mh/temp/test1"
    folder2 = "/Users/mh/temp/test2"
    #folder1 = "/Users/mh/temp/movieposters1"
    #folder2 = "/Users/mh/temp/movieposters2"
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

    compare_folders(folder1, folder2, exclude_files, exclude_extensions)
