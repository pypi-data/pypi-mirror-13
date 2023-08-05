Motivation
==========

*No code here, just opinions and prose.*

Distributed computing is underused.  That's not to say our hardware isn't
occupied (business intelligence tasks will fill every spare cycle) but rather
that there are cases that benefit from distributed hardware but we *just don't
bother* because it's a pain to deal with.

For ad hoc computations in particular we often can't be bothered to write
code in a conceptual framework like MapReduce or Spark (though these get more
accessible year after year.)  We'll just write a script, maybe use multiple
cores on our laptop, and let the job run for a few hours.  We only have to do
this a few times, why bother with all the fuss?

However Spark did a fantastic job to improve the programming API over
MapReduce, and so lowered the conceptual barrier to jump to a distributed
machine.  Many more people use distributed computing today because of Spark's
API improvements over the MapReduce paradigm.  Undoubtedly more frameworks will
arise in the future and improve the situation further.  This is a hard problem
though.  It's hard to make a framework that is simultaneously efficient enough
to use the huge clusters demanded by Big-Data pressure and flexible enough to
fit ad-hoc problems.

This projects development grew out of dask_.  Dask is a parallel computing
system that targets single shared-memory machines.  By not shooting for Big
Data dask is able to drastically lower the barrier


Low barrier to entry is one of the constant pieces of positive feedback we
receive about dask_ (``distributed`` development grew out of ``dask``
development).  People seem to like the following aspects:

1.  Dask is trivial to install and to get started (``conda/pip install dask``)
2.  Dask provides escape hatches when the Spark-like high-level abstractions
    don't easily fit the problem at hand.

However the dask scheduler was single-machine only, and at a certain scale
users had to jettison to some other tool (often Spark.)



Rather there are many problems that could compete
for those precious cycles but don't because we just don't bother to use the
distributed hardware that's available to us.  This is a perfectly reasonable
thing to do; using distributed hardware for



Often we could use distributed computing, but we don't.  Why is this?  What
stops us?

1.


Distributed computation is hard:

1.  **Setup:** It's hard to start up a cluster and often hard to start up
    whatever service you run on that cluster.
2.  **Programming:**

* Lightweight setup/use
* Ad hoc distributed computing.

Today's distributed computing resources are not well utilized by non-experts.



