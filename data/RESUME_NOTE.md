RESUME MODE: an earlier run of this exact task was interrupted. Its partial output file already exists.
1. Load the existing OUT file with Python.
2. Delete from it every entry whose page (page_id, or pdf_page for Habti) is >= the RESUME PAGE given below (that page may be incomplete), and save.
3. Continue the task from the RESUME PAGE to the end of the range, appending to the same array and saving as you go.
Do not touch entries before the RESUME PAGE.
