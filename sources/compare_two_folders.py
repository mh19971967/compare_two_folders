#!/usr/bin/env -S python3 -u

"""
Program                      : ctf.py
Author                       : Maro Hartmann (partly chatGPT)
Date                         : 2023.03.17
Version                      : 2023.03.17.1
Python Version, Mac OS X     : 3.11
Python Version, Raspberry Pi : 3.11

Issue Log:


Starting the script:
./ctf.py


Required packages in PyCharm and Raspberry Pi:
Name                         Type               Mac/Raspi Version  Dependencies  VersionCheckCommand
------------------------------------------------------------------------------------------------------------------------
os                           standard-library   latest             -             -
datetime                     standard-library   latest             -             -
"""

import os
import datetime

from ctf_functions import (
    print_verbose,
    search_file,
    compare_files,
    evaluate_file_comparison_state,
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
                    def_verbose["details"] and def_verbose["files-pass"],
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
                f"{def_info_text}: '{file}' in '{path}'"
            )
        if def_files.items():
            print()
        return count_files

    def print_files_missing_with_search(
        def_files,
        def_info,
    ):
        count_files = 0
        for idx, (file, path) in enumerate(
            def_files.items(),
            1,
        ):
            count_files += 1
            file_name_only = os.path.basename(file)
            path_only = os.path.dirname(path)
            file_found_in_source = search_file(
                file_name_only, search_path=def_folder_source
            )
            file_found_in_target = search_file(
                file_name_only, search_path=def_folder_target
            )
            if file_found_in_source and file_found_in_target:
                results = compare_files(
                    file_found_in_source,
                    file_found_in_target,
                    def_hash_algorithm,
                    def_options,
                )
                file_found_in_folder = {
                    "source": file_found_in_source,
                    "target": file_found_in_target,
                }

                file_identical = all((item["result"] for item in results))
                if file_identical:
                    print()
                    print(
                        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                        f"ERROR->OK: File missing in {def_info}: '{file_name_only}' in '{path_only}'"
                    )
                    print(
                        f"                     -> but found in {def_info} folder: {file_found_in_folder[def_info]}"
                    )
                    print("                     -> and are identical: OK")
                    print(
                        f"                     -> check source file: {file_found_in_source}\n",
                        f"                    -> check target file: {file_found_in_target}",
                    )
                    for detail in results:
                        print_verbose(
                            f"                     -> {detail}",
                            def_verbose["details"],
                        )
                    print()
                else:
                    print()
                    print(
                        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                        f"ERROR:     File missing in {def_info}: '{file_name_only}' in '{path_only}'"
                    )
                    print(
                        f"                     -> but found in {def_info} folder: {file_found_in_folder[def_info]}"
                    )
                    print("                     -> but are NOT identical: ERROR")
                    print(
                        f"                     -> check source file: {file_found_in_source}\n",
                        f"                    -> check target file: {file_found_in_target}",
                    )
                    for detail in results:
                        print_verbose(
                            f"                     -> {detail}",
                            def_verbose["details"],
                        )
                    print()
            else:
                print(
                    f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                    f"ERROR:     File missing in {def_info}: '{file_name_only}' in '{path_only}'"
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
                print_verbose(
                    f"                     -> {detail}",
                    def_verbose["details"],
                )
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
                f"ERROR:     File differs:           '{file}':"
            )
            for detail in details:
                print_verbose(
                    f"                     -> {detail}",
                    def_verbose["details"],
                )
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
            "details": True,
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
    count_files_missing_in_source = print_files_missing_with_search(
        files_missing_source,
        "source",
    )

    # Printing all files missing in target
    count_files_missing_in_target = print_files_missing_with_search(
        files_missing_target,
        "target",
    )
    # TODO: COPY TO TARGET?

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

    # folder1 = "/Users/mh/temp/test1"
    # folder2 = "/Users/mh/temp/test2"
    # folder1 = "/Users/mh/temp/movieposters1"
    # folder2 = "/Users/mh/temp/movieposters2"
    # folder1 = "/Users/mh/temp/01 - Januar"
    # folder2 = "/Users/mh/temp/02 - Januar"
    # folder1 = "/Volumes/Untitled"
    # folder2 = "/Users/mh/Documents/DJI Mini 3 Pro/DJI Mini 3 Pro"
    # folder1 = "/Users/mh/Documents/Bilder/Diverse Fotos"
    # folder2 = "/Volumes/ASRDataVolume_12004 - Daten/Users/mh/Documents/Bilder/Diverse Fotos"
    folder1 = "/Users/mh/ownCloud/HM/Ulmenstrasse 16"
    folder2 = "/Users/mh/ownCloud - hm@192.168.1.5/Ulmenstrasse 16"

    # Optional: specify a list of files to exclude
    # exclude_files = []
    exclude_files = [".DS_Store"]

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
        "files-pass": False,
        "details": True,
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

        sum_source_check = (
            number_files_any_difference_but_mtime
            + number_files_only_mtime_difference
            + number_files_pass
            + number_files_missing_in_target
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files in source:                                "
            f"'{sum_source:{digits_num_files}}' (checked: {sum_source_check})",
            verbose["summary"],
        )
        sum_target_check = (
            number_files_any_difference_but_mtime
            + number_files_only_mtime_difference
            + number_files_pass
            + number_files_missing_in_source
        )
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"Number of files in target:                                "
            f"'{sum_target:{digits_num_files}}' (checked: {sum_target_check})",
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
