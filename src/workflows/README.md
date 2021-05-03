Implementation requirements
===========================

1. Ease of transfer from bifx to SW -> Computation and GUI rendering steps must be detangled

Required functionality
======================

1. A complete initialization on loading the sample the first time? Maybe each assay should be loaded separately
2. Caching of each step to avoid recomputation.
3. If initialization fails, present a UI to continue from where it stopped.


How strict should we be about the implementation details crossing from one class to another
	1. Can the compute class rerun the interface?
	2. Can the compute class raise interface exceptions

One that is enforced is that all arguments shared between Render and Compute have to be declared in Arguments