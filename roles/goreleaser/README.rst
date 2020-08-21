Invoke goreleaser

Invoke goreleaser with different options optionally also importing gpg key for artifacts signing and pushing to github

**Role Variables**

.. zuul:rolevar:: goreleaser_args
   :default: --snapshot --rm-dist

   goreleaser arguments

.. zuul:rolevar:: goreleaser_sign
   :default: False

   Whether gpg import for signing should be enabled or not

.. zuul:rolevar:: gpg_key
   :default: none

   GPG key to import for artefacts signing
