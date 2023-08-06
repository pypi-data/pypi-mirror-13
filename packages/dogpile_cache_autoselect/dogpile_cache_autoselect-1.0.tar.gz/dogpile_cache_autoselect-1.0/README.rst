
Autoselect dogpile.cache backends
-----------------------------------------

This consists of one function that tries to detect dogpile.cache backends and chooses the best one.

The function::

	auto_select_backend(region_kwargs=None, between_runs=True, require_server=False, verbose=False)

Use like this:

* region_kwargs: Parameters passed on to the region (dictionary).
* between_runs: If True, only selects backends that persist between runs.
* require_server: If True, raises an exception if no working server-backend is found (redis, memcached).
* verbose: If True, prints choices that are being made.

Typically::

	backend = auto_select_backend()
	# done

It can only detect backends that don't need special parameters to connect to (so it has to run locally). It's mostly for software distributed to people who'll run it locally (if you've set up a big caching cluster, you can probably spare 1 more minute to configure dogpile).



