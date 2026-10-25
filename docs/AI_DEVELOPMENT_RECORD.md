# AI use and development provenance

OpenAI ChatGPT materially assisted with planning, writing and refactoring Python
notebook cells, suggesting nearest-neighbour and IDW comparisons, selecting
validation designs, correcting common-support bias, debugging runtime errors,
producing result visualisations, creating source-code tests, drafting this report,
and proposing Git structure and commands.

The project was first developed in Google Colab. It was subsequently organised
into a Git repository for submission. The real commit history should be interpreted as steps actually committed,
not an invented history of earlier Colab development.

Examples of AI suggestions or generated code corrected during development:
- Initial Colab notebook referred to a locally absent `apple_tree` package.
  Notebook 01 was revised to use PIL/NumPy instead.
- A depth-labelled PNG stored identical values in three RGB channels; the
  loader was revised to check channel equality rather than rejecting all RGB.
- Notebooks sometimes failed because `selection`, `make_split`, or an uploaded
  ZIP was missing in a new runtime. Standalone setup and upload steps were added.
- Per-method RMSE used different sets of supported pixels. A common-support
  follow-up corrected the comparison design.
- Plot labels were corrected to convert saved seconds into milliseconds.

The student supplied inputs, accessed the permitted dataset, executed Colab
experiments, reported errors, and decided which simplifications to retain.
AI-generated code and claims remain subject to software tests, visual inspection,
and the student author’s responsibility. AI contributed substantially rather
than only providing proofreading. The original 3D skeleton objective remains
unfinished; the final numerical study addresses a narrower depth reliability
question. The raw depth codes were not calibrated to metres.

For a fuller account, see the report section on responsible AI use.
