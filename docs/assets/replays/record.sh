#!/usr/bin/env bash
# One .bmmreplay per documented feature, recorded from the real BMM over its local API.
#
# WHY THE APP IS KILLED AND RELAUNCHED PER RECORDING
#
# rrweb emits its Meta and FullSnapshot only when a session genuinely starts. Without them a
# replay is a list of mutations with nothing to apply them to — two early attempts produced
# 44- and 37-event files no player can open. A cold start is also what gives each recording
# BMM's own intro, which is the point of doing this at all.
#
# `POST /api/restart` looked like the way to get one and is not. Under `tauri dev` it kills
# the app for good; the API answers for a couple of seconds on the dying process, long enough
# for one export to land and for every later one to write nothing. Killing the process here
# and starting it again is boring, observable, and works — proven by hand before this script
# was written.
#
# WHY THE VERIFICATION IS WHAT IT IS
#
# An earlier run reported success thirteen times while writing nothing. The check was
# `[ -f "$dest" ]`, and placeholders of the same names had sat in that folder since July, so
# it confirmed a file existed and never that this run produced it. Each recording is now
# checked for mtime newer than its own start, for parsing, for carrying a FullSnapshot, and
# for the masked flag matching what was asked for.
#
# Navigation only. No mod is enabled, no profile switched, nothing on disk is touched.

set -u
T="${BMM_TOKEN:?set BMM_TOKEN}"
B="http://127.0.0.1:51274"
# Both overridable, so this is not tied to one machine.
#   BMM_TOKEN=<Settings -> Plugin API>  BMM_EXE=... OUT_DIR=... ./record.sh
#   ONLY="mapper themes" ./record.sh     re-record a subset
EXE="${BMM_EXE:-$(cd "$(dirname "$0")/../../../.." && pwd)/src-tauri/target/release/better-mods-manager.exe}"
OUT="${OUT_DIR:-$(cd "$(dirname "$0")" && pwd)}"

post() { curl -s -m 10 -o /dev/null -w "%{http_code}" -X POST \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "$2" "$B$1"; }
up()   { curl -s -m 2 -o /dev/null "$B/api/health" 2>/dev/null; }

kill_bmm() { taskkill //F //IM better-mods-manager.exe >/dev/null 2>&1; sleep 3; }

start_bmm() {
  ( "$EXE" >/dev/null 2>&1 & )
  for _ in $(seq 1 45); do sleep 2; up && return 0; done
  return 1
}

tour() {
  case "$1" in
    scheduler|themes) echo "settings" ;;
    bmm-demo) echo "library profiles modpacks mapper repo modlist apps plugins community settings" ;;
    *) echo "$1" ;;
  esac
}

verify() {
  node -e '
const fs=require("fs"),f=process.argv[1],since=+process.argv[2];
if(!fs.existsSync(f)){console.log("  BAD: no file");process.exit(1)}
const st=fs.statSync(f);
if(st.mtimeMs/1000 < since){console.log("  BAD: not written by this run (mtime "+st.mtime.toISOString()+")");process.exit(1)}
let d;try{d=JSON.parse(fs.readFileSync(f,"utf8"))}catch(e){console.log("  BAD: unparseable");process.exit(1)}
const c={};for(const e of d.events||[])c[e.type]=(c[e.type]||0)+1;
if(!c[2]){console.log("  BAD: no FullSnapshot - unplayable");process.exit(1)}
if(d.masked!==false){console.log("  BAD: masked="+d.masked+" (wanted unmasked)");process.exit(1)}
const m=(d.events||[]).find(e=>e.type===4);
console.log("  ok "+(st.size/1048576).toFixed(1)+" MB, "+d.events.length+" events, "+
            (m?m.data.width+"x"+m.data.height:"?")+", masked=false");
' "$1" "$2"
}

# The recorder flag lives in localStorage and survives a restart, so it is set once.
up || start_bmm || { echo "BMM will not start"; exit 1; }
post /api/recorder '{"on":true,"full":true}' >/dev/null
sleep 2

fails=0
for name in ${ONLY:-library profiles modpacks mapper repo modlist apps plugins community settings scheduler themes bmm-demo}; do
  dest="$OUT/$name.bmmreplay"
  echo "=== $name ==="
  stamp=$(date +%s)
  kill_bmm
  if ! start_bmm; then echo "  FAILED: BMM did not start - stopping"; exit 2; fi
  sleep 12                                  # cold window: intro plays, spool starts filling
  for v in $(tour "$name"); do
    post /api/view "{\"id\":\"$v\"}" >/dev/null
    sleep 3
  done
  sleep 2
  post /api/replay/export "{\"path\":\"$dest\"}" >/dev/null
  sleep 8                                   # the write is async behind a 202
  verify "$dest" "$stamp" || fails=$((fails+1))
done
kill_bmm
echo "ALL DONE - $fails failure(s)"
