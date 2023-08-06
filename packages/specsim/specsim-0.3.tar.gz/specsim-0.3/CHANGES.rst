0.3 (2016-02-19)
----------------

This version introduces some significant API changes in order to make the
code instrument agnostic and facilitate future algorithm improvements.
There are no changes yet to the underlying algorithms and assumptions, so
results using the new desi.yaml config should be identical to v0.2.

- Add new config module for flexible specification of all simulation options,
  including the instrument model definition.
- Create config files for DESI and unit testing.
- Refactor to make code instrument-agnostic, with no dependencies on
  DESI packages.
- Read files using astropy.table.Table.read() instead of numpy.loadtxt()
  and astropy.io.fits.read().
- Remove unused sources, spectrum modules.
- Rename quick.Quick to simulator.Simulator.
- Add speclite dependency.

0.2 (2015-12-18)
----------------

- Add the transform module for coordinate transformations between the sky,
  alt-az, and the focal plane.
- Minor improvements to sparse resolution matrix edge effects.
- Provide per-camera flux and ivar predictions.

0.1 (2015-09-16)
----------------

- Initial release after migration from desimodel SVN.
- Gives identical results to quicksim.
