Use the Bash tool to read the selected test case from /tmp/tc_pick:

```
cat /tmp/tc_pick
```

If the file is empty or missing, tell the user to run `bash pick-tc.sh` in another terminal/zellij pane first, then trigger `/analyze-tc` again.

Once a SQL file path is obtained:

1. Derive the related file paths:
   - `CASES_DIR` = directory of the SQL file
   - `TC_NAME` = basename without `.sql`
   - `ANSWER_FILE` = `${CASES_DIR%/cases}/answers/${TC_NAME}.answer`
   - `RESULT_FILE` = `${CASES_DIR}/${TC_NAME}.result`

2. Use the Read tool to read all three files: the `.sql`, `.answer`, and `.result` files.

3. Analyze the failure:
   - What the test is trying to verify (based on the SQL)
   - What went wrong (compare expected vs actual output)
   - The likely root cause of the failure

Be specific and technical. Reference exact lines from the diff where relevant.
