# youtube-copyright-to-timestamps
Convert the text from the Youtube Studio copyright section into usable timestamps in the description!

# Usage - copyright-to-timestamps
1. take something that looks like ![./docs/sample.png](./docs/sample.png)
2. Drag from the "Content used" | "Impact on the video" columns, and paste it in a file like [./docs/copyright.txt](./docs/copyright.txt)
3. run the following to get nice output
    ```bash
    python main.py sample.txt
    ```
    ```txt
    00:04:06 - Rome In Silver - Fool
    00:05:03 - Kanye West - Fade
    00:05:58 - Justice - Helix
    00:08:01 - Skrillex, Starrah, Four Tet - Butterflies (Extended Mix)
    00:10:11 - Madeon - Technicolor
    00:12:17 - Justice, Simian - We Are Your Friends (Justice Vs. Simian)
    00:21:26 - Daft Punk - One More Time (Radio Edit)
    00:23:14 - Virtual Self - ゴースト・ヴォイセズ
    00:24:48 - Modjo - Lady (Hear Me Tonight) (Hear Me Tonight)
    00:26:52 - DJ Snake - U Are My High
    00:28:41 - Justice - Safe and Sound (WWW)
    ```
# Usage - timestamp-offsetter
1. take something that looks like this and save it in a file like [./docs/timestamps.txt](./docs/timestamps.txt)
    ```
    Timestamps
    01:01:10 - Heavy with Hoping
    01:05:05 - Piano Solo
    01:06:01 - Borealis
    01:08:47 - Miracle
    01:13:44 - Shelter x All My Friends
    ```
2. Figure out how much offset you want in seconds, eg) -60 +120, etc
3. run the following to get nice output
    ```bash
    python timestamp-offsetter.py docs/timestamps.txt -369
    ```
    ```txt
    00:55:01 - Heavy with Hoping
    00:58:56 - Piano Solo
    00:59:52 - Borealis
    01:02:38 - Miracle
    01:07:35 - Shelter x All My Friends
    ```


# TODO:
1. combine into 1 app...