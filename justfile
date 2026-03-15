# test-sql-autoreport justfile
# Usage: just <recipe> [args]

pr    := "https://github.com/CUBRID/cubrid/pull/6904"
src   := "/home/vimkim/gh/tc/cubrid-testcases/"
dest  := "./failed_tcs"
list  := "failed_tc_list.txt"

# Show available recipes
default:
    @just --list

# Fetch failed TC list from a PR and save to failed_tc_list.txt
# Usage: just fetch pr=https://github.com/CUBRID/cubrid/pull/6904
fetch:
    @test -n "{{pr}}" || (echo "Error: pr= is required. Usage: just fetch pr=<url>" && exit 1)
    uv run get_failed_tc_list_from_pr.py {{pr}} | tee {{list}}

# Copy failed TCs from source dir to dest dir
# Usage: just clone src=/path/to/cubrid/sql
clone:
    @test -n "{{src}}" || (echo "Error: src= is required. Usage: just clone src=<dir>" && exit 1)
    uv run clone_failed_tc.py -l {{list}} -s {{src}} -d {{dest}}

# Full pipeline: fetch failed TCs from PR, then clone them from source dir
# Usage: just run pr=https://github.com/CUBRID/cubrid/pull/6904 src=/path/to/cubrid/sql
run:
    @test -n "{{pr}}"  || (echo "Error: pr= is required"  && exit 1)
    @test -n "{{src}}" || (echo "Error: src= is required" && exit 1)
    just fetch pr={{pr}} list={{list}}
    just clone src={{src}} dest={{dest}} list={{list}}

# Remove generated output files
clean:
    rm -f {{list}}
    rm -rf {{dest}}
