# 0002: Where each data source is pulled from

**Date:** 2026-11-27
**Status:** Accepted

## Context

There are three data sources:

1. **NBA stats** from stats.nba.com, through the `nba_api` package.
2. **The official NBA injury report**, through the `nbainjuries` package.
3. **My ESPN fantasy league**, through the `espn-api` package. It needs my `espn_s2` and `SWID` login cookies.

Two things limit where these can run:

- On Databricks Free Edition, serverless compute can only reach a short list of allowed websites, and Databricks doesn't publish that list.
- stats.nba.com blocks requests from cloud servers.

## What we tested

| Source | From my laptop | From a Databricks notebook |
|---|---|---|
| NBA stats (`nba_api`) | Works | Blocked |
| NBA injury report (`nbainjuries`) | Works (needs Java) | Blocked |
| ESPN fantasy league (`espn-api`) | Not needed | Works |

## Decision

Each source is pulled from the place where it works, and **every source lands its raw files in the same place, in the same layout**:

- **NBA stats and injuries:** a script on my laptop pulls them, saves the raw JSON, and uploads it to the Unity Catalog volume.
- **ESPN league:** a Databricks job pulls it, using the cookies from the `nba` secret scope, and writes the raw JSON to the same volume.
- **The landing path** is `/Volumes/nba_<env>/bronze/raw/<source>/<name>_<UTC timestamp>.json`.
- **Auto Loader** then reads every source from that volume into the bronze tables. Everything after the volume is the same no matter where the data came from.

## Why

- **The volume is the single entry point.** The pipeline doesn't need to know whether a file came from my laptop or from Databricks.
- **ESPN runs in Databricks because it can.** It's scheduled by Databricks, reads its cookies from the secret scope, and doesn't depend on my laptop being on.
- **NBA stats and injuries have no cloud option.** They're blocked from Databricks. A paid API (such as BALLDONTLIE) was the alternative, and wasn't worth paying for.

## Things to know about the raw data

- **NBA stats** arrive as column headers plus rows (`resultSets` → `headers`, `rowSet`), not as one record per row. The silver layer has to turn them into rows.
- **Injury report** player names are written "Last, First" (e.g. "Antetokounmpo, Giannis"). Matching them to NBA stats players needs name cleaning.
- **ESPN** player IDs are different from NBA.com IDs. The silver layer needs a table that maps one to the other.

## Consequences

- **The NBA stats and injury data only update when my laptop runs the script.** This needs a schedule on the laptop (e.g. Windows Task Scheduler). If the laptop is off, those sources fall behind until the next run.
- **Not tested yet:** uploading a file from the laptop to the volume (Databricks CLI or SDK). That's the next step.
- **ESPN news** isn't part of this decision. We'll revisit it later.
