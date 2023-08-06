# fava: CHANGES

*Note: This file contains only user-facing changes in the 'master' branch.*

2016-02-15

  - Installing via `pip install beancount-fava` now works, all requirements
    included. Bumped version to 0.2.3 to communicate that. (Thanks to Martin
    Blais for fixing the beancount setuptools issue and Jakob Schnitzer for the
    PR)

2016-02-13

  - Bumped version to 0.2.1 due to changes in how JavaScript and CSS are
    handled internally (Thanks to Jakob Schnitzler for the work!).

2016-02-11

  - Renamed the project from "beancount-web" to "fava" (Issue #85)

  - Moved `beancount-urlscheme`-command to it's own project (see [github.com/au
    mayr/beancount_urlscheme](http://github.com/aumayr/beancount_urlscheme) for
    details).

2016-01-30

  - `Today` wasn't included in `Year to Date` filter - now it is. (Thanks to
    Daniel Bos for the PR)

  - Legs now collapse correctly in the Journal view. (Thanks to Daniel Bos for
    the PRs)

2016-01-20

  - New favicon (Issue #90)

2016-01-18

  - Display QUERY directives in a dropdown in the Custom Query view (Issue
    #96). (Thanks to Daniel Bos and Jakob Schnitzer for the help)

2016-01-14

  - Prevent metadata keys from linewrapping

2016-01-11

  - Filters were previously shown on all pages, even those where they didn't
    make sense or do anything. Now they got removed from pages such as `Custom
    Query`, `Source`, `Options`, and `Errors` (Issue #97). (Thanks to Daniel Bos for the PR)

2016-01-09

  - Added Windows/Cygwin-support to `beancount-urlscheme` (Issue #92). (Thanks
    to redstreet for the PR)

2016-01-07

  - New setting `collapse-accounts` to specify a list of accounts to
    collapse in the account hierachy (tree-tables) (Issue #91).

  - Added new `beancount-urlscheme`-command to register the `beancount://`-URL
    -scheme on a Mac (other platforms still missing, but in development). There
    is a new setting called `use-external-editor` that will, if set to `True`,
    render all links to the Source Editor als `beancount://`-URLs to open the
    files directly in the editor specified by the `external-editor-cmd`-setting
    (The URL-scheme has to be registerd with `beancount-urlscheme` first). This
    also renders the Source Editor view as readonly (Issue #92).

2015-12-28

  - Added new setting (and feature) called `editor-insert-marker`. If present,
    the Source editor will jump to the specified marker (like
    `;;; INSERT HERE`) and will insert two newlines above it and set the cursor
    there (Issue #76).

  - Bar chart bars are now clickable and will set the time filter to the year
    and month the bar is representing.

  - Line charts are now zoomable by drawing a rectangle with the mouse on the
    chart, which will then zoom to the specified area.

  - Added keyboard shortcuts for jumping to menu items, open and focus
    filters, Journal entry types and more. Press <kbd>?</kbd> to display
    an overview of all keyboard shortcuts (Issue #65). (Thanks to redstreet
    for the suggestions)

2015-12-27

  - Source editor now supports auto-completion of accounts, commodities,
    directives and tags.

2015-12-25

  - Entries can now be filtered for "No payee" (Issue #42). (Thanks to Jakob
    Schnitzer for the PR)

2015-12-24

  - Metadata is now displayed for Journal entries. For transactions, if there
    is a metadata-entry called "statement" and it's value is a path to a file
    (relative to the beancount-file or absolute), this file will be liked.

2015-12-23

  - Up-to-date indicator will be shown for Assets- and Liabilities-accounts
    in the Statistics view that indicates:

        green:  The latest posting is a balance check that passed (known-good)
        red:    The latest posting is a balance check that failed (known-bad)
        yellow: The latest posting is not a balance check (unknown)
        gray:   The account hasn't been updated in a while (as compared to the
                last available date in the file)

    There are corresponding settings to show the indicator in all other views
    (Balance sheet, etc.), to change the days for the look-back (yellow vs gray)
    and to exclude certain accounts from displaying the indicator.

  - New settings to show Journal legs by default, to show different entry types
    in a Journal by default, to hide charts by default and to show negative
    numbers in treemaps

  - Added new command line option "--settings" to specify a settings-file for
    beancount-web, like which entry types to display in a Journal by default.
    There is a sample file called "default-settings.conf" in the source that
    lists all possible settings.

  - Filters are now part of every URL, so every URL is a permalink to the
    view including all currently set filters (Issue #54). (Thanks to Jakob
    Schnitzer for the work on this)

2015-12-22

  - Fixed minor styling issues.

2015-12-21

  - Custom BQL queries (like with `bean-query`) can now be run in a new
    Custom Query view. The results will be displayed as a table and somewhat
    formatted, as account names will be linked to the Account view for example.

2015-12-20

  - Simple tables (Equity/Holdings, Net Worth, Events, Commodities, Options,
    Statistics, Errors) are now sortable by clicking on the column headers
    (Issue #46).

  - Added a yearly balances table to the Account-view. (Thanks to David
    Stephens for the PR)

  - Limited the number of x-axis-labels for bar charts to a maximum of 25
    (Issue #45).

  - Fixed a minor bug where treemaps would show white areas (Issue #49).

  - Fixed daterange filtering of entries. (Thanks to Jakob Schnitzer for the PR)

  - Fixed values in Balance sheet to correctly calculate the closing balances
    (Issue #19).

2015-12-19

  - Added a permalink for the currently set filters, so a user can bookmark
    different filter-settings for quickly applying them (Issue #26).

(Beginning to summarize user-facing changes 2015-12-19.)
