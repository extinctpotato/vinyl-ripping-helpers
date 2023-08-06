import pyinputplus as pyip
from pathlib import Path
from vriphelper.tags import TaggableProject
from vriphelper.term import ReorderableTable
from vriphelper.misc import Backwardable

def ask_for_tags(input_path: Path):
    t = TaggableProject(input_path)

    print(f"Input path:\t {input_path}")
    print(f"Loaded {len(t.files)} file(s).")

    def __common_artist():
        current_value = t.get_common_key("artist")
        if (common_artist := pyip.inputStr(f"Provide a common artist for all tracks (leave empty if unapplicable) [{current_value}]: ", blank=True)):
            t.set_common_artist(common_artist)
            print(f"Set '{common_artist}' for all tracks.")

    def __common_year():
        current_value = t.get_common_key("date")
        if (common_year := pyip.inputInt(f"When was this {t.release_type} released? [{current_value}] ", blank=bool(current_value))):
            t.set_common_year(common_year)
            print(f"Set {common_year} as the release year.")

    def __common_album():
        current_value = t.get_common_key("album")
        if (common_album := pyip.inputStr(f"Provide a common album for all tracks (leave empty if unapplicable) [{current_value}]: ", blank=True)):
            t.set_common_album(common_album)
            print(f"Set '{common_album}' for all tracks.")

    def __set_artist_gen(idx: int):
        def __inner():
            if t.get_common_key("artist"):
                print(f"[{t.files[idx].filename}] Common artist has already been set, skipping.")
                return True

            current_value = t.files[idx].get("artist")
            if (v := pyip.inputStr(f"[{t.files[idx].filename}]\t Artist name: ({current_value})", blank=True)):
                t.set_artist(idx, v)
        return __inner

    def __set_title_gen(idx: int):
        def __inner():
            current_value = t.files[idx].get("title")
            if (v := pyip.inputStr(f"[{t.files[idx].filename}]\t Title: ({current_value})", blank=True)):
                t.set_title(idx, v)
        return __inner

    def __should_commit():
        if pyip.inputBool("Should we commit? "):
            t.commit()

    def __should_set_tracks():
        file_table = ReorderableTable(
                title=t.get_common_key("artist") + " - " + t.get_common_key("album"),
                columns=["Track number", "File name"],
                rows=enumerate([tr.filename for tr in t.files], 1)
                )
        file_table.inquire()

        for idx, row in enumerate(file_table.rows):
            t.set_track_number(int(row[0]) - 1, idx)

        t.sort_files()

    def __should_rename():
        for idx, _ in enumerate(t.files):
            try:
                print(f"[{idx}]: {t.get_formatted_filename(idx)}")
            except ValueError as e:
                print(f"[{idx}]: EXCEPTION! {e}")
        if pyip.inputBool("Should we rename? "):
            t.rename_files()

    wizard_queries = [
            __common_artist,
            __common_album,
            __common_year,
            __should_set_tracks
            ]
    for f_idx, _ in enumerate(t.files):
        for gen in [__set_artist_gen, __set_title_gen]:
            wizard_queries.append(gen(f_idx))
    wizard_queries.append(__should_commit)
    wizard_queries.append(__should_rename)

    b = Backwardable(wizard_queries)
    prev_enq = False
    for func in b:
        print(f"Running question {b.pos}/{len(b)}")
        was_skipped = func()

        if was_skipped:
            if prev_enq:
                b.queue_previous()
            continue

        prev_enq = False

        if (next_action := pyip.inputMenu(['next', 'previous', 'repeat'], lettered=True)) == 'next':
            pass
        elif next_action == 'previous':
            b.queue_previous()
            prev_enq = True
        elif next_action == 'repeat':
            b.queue_repeat()
