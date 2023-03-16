import blake3

data = b"Hello, world!"
hash_object = blake3.blake3(data)
print(hash_object.hexdigest())


F1 = "/Users/mh/temp/test1/2023-02-01_Hamburger_Abendblatt_Hamburg_-_01-02-2023.pdf"
C1 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "11797760",
        "file2_data": "11797760",
    },
    {
        "details": "file_mtime",
        "result": False,
        "file1_data": "2023-02-10 17:02:22",
        "file2_data": "2023-02-13 20:40:17",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "0e1434bf809a1db375c32a28bc7a3d2438215191ce3d20e217815bd199a5a44a2a884f5ca1f612118b0cd686fd5295ea41053b727bf8f4ffb969915856822581",
        "file2_data": "0e1434bf809a1db375c32a28bc7a3d2438215191ce3d20e217815bd199a5a44a2a884f5ca1f612118b0cd686fd5295ea41053b727bf8f4ffb969915856822581",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]
R1 = ""

F2 = "/Users/mh/temp/test1/test.pdf"
C2 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "10048545",
        "file2_data": "10048545",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:01:57",
        "file2_data": "2023-02-10 17:01:57",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "bab614a5c44f04ec950a9b71572154402c98bbfefc801815bff78fd0d07b81fe5a74f7ef9bb95333d66aa2ec63b59697d2b631600c69af9e7d3420983cda9a36",
        "file2_data": "bab614a5c44f04ec950a9b71572154402c98bbfefc801815bff78fd0d07b81fe5a74f7ef9bb95333d66aa2ec63b59697d2b631600c69af9e7d3420983cda9a36",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F3 = "/Users/mh/temp/test1/gelesen/2023-02-03_Hamburger_Abendblatt_Hamburg_-_03-02-2023.pdf"
C3 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "10048545",
        "file2_data": "10048545",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:01:57",
        "file2_data": "2023-02-10 17:01:57",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "bab614a5c44f04ec950a9b71572154402c98bbfefc801815bff78fd0d07b81fe5a74f7ef9bb95333d66aa2ec63b59697d2b631600c69af9e7d3420983cda9a36",
        "file2_data": "bab614a5c44f04ec950a9b71572154402c98bbfefc801815bff78fd0d07b81fe5a74f7ef9bb95333d66aa2ec63b59697d2b631600c69af9e7d3420983cda9a36",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F4 = "/Users/mh/temp/test1/2023-02-09_Hamburger_Abendblatt_Hamburg_-_09-02-2023.pdf"
C4 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "12451994",
        "file2_data": "12451994",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-09 17:54:37",
        "file2_data": "2023-02-09 17:54:37",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "ddcaf5e0e970389ad0628ed3f0206e47260132b5afd75426b7d7fb0e4bf630e09ed1d2f53f25cda821e4af6310b88df171eb183d85eecfa1d04d1f5c2cc8c4f7",
        "file2_data": "ddcaf5e0e970389ad0628ed3f0206e47260132b5afd75426b7d7fb0e4bf630e09ed1d2f53f25cda821e4af6310b88df171eb183d85eecfa1d04d1f5c2cc8c4f7",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F5 = "/Users/mh/temp/test1/2023-02-08_Hamburger_Abendblatt_Hamburg_-_08-02-2023.pdf"
C5 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "10175588",
        "file2_data": "10175588",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:01:02",
        "file2_data": "2023-02-10 17:01:02",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "2e62eac6c3a20fe864a7bb7e2592cd6b153301f5804c834e8f90dc9dcc2d05fa4a46cb93e9f4dbe910439dea42dbe604f27b6e72624b206ea8f5e903db156e7a",
        "file2_data": "2e62eac6c3a20fe864a7bb7e2592cd6b153301f5804c834e8f90dc9dcc2d05fa4a46cb93e9f4dbe910439dea42dbe604f27b6e72624b206ea8f5e903db156e7a",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F6 = "/Users/mh/temp/test1/gelesen/2023-02-07_Hamburger_Abendblatt_Hamburg_-_07-02-2023.pdf"
C6 = [
    {
        "details": "file_size",
        "result": False,
        "file1_data": "8158804",
        "file2_data": "23445233",
    },
    {
        "details": "file_mtime",
        "result": False,
        "file1_data": "2023-02-10 17:01:14",
        "file2_data": "2023-02-10 17:01:40",
    },
    {
        "details": "file_hash",
        "result": False,
        "file1_data": "543d487f33d9c3f1fb6ca655d1a4a8bd3978b891c10e2bee672cd8d05dc287cfba2ab59c11cf8c7074f33cb44e8748955042569091cba945de0b134b48ff0c8c",
        "file2_data": "da3647a263b11389c86fc895d89fcc9de1645532819b3585ff50161b77a470f33cfb41f51a66aa7f1a001c484c605f0a4cc5a7deabdbad7ee71f20332b0debb3",
    },
    {"details": "file_bit", "result": False, "file1_data": "", "file2_data": ""},
]

F7 = "/Users/mh/temp/test1/2023-02-06_Hamburger_Abendblatt_Hamburg_-_06-02-2023.pdf"
C7 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "9891978",
        "file2_data": "9891978",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:01:25",
        "file2_data": "2023-02-10 17:01:25",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "edaaf574645f27094eca3e042faa5163a1d7d3c9483b488404c160e6a3f5edd372a2debaaef421645ae7c44d477d115a8c0db4cd4c28de3a4979f28bf7899d0e",
        "file2_data": "edaaf574645f27094eca3e042faa5163a1d7d3c9483b488404c160e6a3f5edd372a2debaaef421645ae7c44d477d115a8c0db4cd4c28de3a4979f28bf7899d0e",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F8 = "/Users/mh/temp/test1/.DS_Store"
C8 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "6148",
        "file2_data": "6148",
    },
    {
        "details": "file_mtime",
        "result": False,
        "file1_data": "2023-02-16 19:28:32",
        "file2_data": "2023-02-12 13:16:42",
    },
    {
        "details": "file_hash",
        "result": False,
        "file1_data": "d65be7ecb0be7430c06842db8920b33ceabd4e4af9e64e3f6fc24f5f083e3ba6645d95414d58653e51f13c76f707868cbb6a6408a7fd1d8774c8a8d7e5743c5b",
        "file2_data": "861832b879667564da7b958cbb592ce097791538b2b4fec8446a7714a8a71376bcbfdb398ddd6a8a080de2044b333c81b2e314bfaa5c130ce95826b50e869692",
    },
    {"details": "file_bit", "result": False, "file1_data": "", "file2_data": ""},
]

F9 = "/Users/mh/temp/test1/2023-02-10_Hamburger_Abendblatt_Hamburg_-_10-02-2023.pdf"
C9 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "12419807",
        "file2_data": "12419807",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:00:51",
        "file2_data": "2023-02-10 17:00:51",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "422a78e5076f334b5a6e64204b55b25ae6304ca5d44899828727e113415fa620b7c336deb1749d800a8745b709548764cc7674615b2dcb7f624fa2fc2e6de64d",
        "file2_data": "422a78e5076f334b5a6e64204b55b25ae6304ca5d44899828727e113415fa620b7c336deb1749d800a8745b709548764cc7674615b2dcb7f624fa2fc2e6de64d",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]

F10 = "/Users/mh/temp/test1/2023-02-02_Hamburger_Abendblatt_Hamburg_-_02-02-2023.pdf"
C10 = [
    {
        "details": "file_size",
        "result": True,
        "file1_data": "13859826",
        "file2_data": "13859826",
    },
    {
        "details": "file_mtime",
        "result": True,
        "file1_data": "2023-02-10 17:02:11",
        "file2_data": "2023-02-10 17:02:11",
    },
    {
        "details": "file_hash",
        "result": True,
        "file1_data": "512fe2582e2d6347da54008e480887b0c016f5d925475171cae9e2c4b2768fef496709df6098167ba9c780d7d369c71f433dd210f0dc8939428823a55b8277ef",
        "file2_data": "512fe2582e2d6347da54008e480887b0c016f5d925475171cae9e2c4b2768fef496709df6098167ba9c780d7d369c71f433dd210f0dc8939428823a55b8277ef",
    },
    {"details": "file_bit", "result": True, "file1_data": "", "file2_data": ""},
]
