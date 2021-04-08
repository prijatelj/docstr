"""Metaprogramming for expediting common tasks using parsed docstrings."""

# TODO decorator for filling in args and kwargs from the docstring. Write once.
#   Below is an example proof of concept pulled from HWR with novelty work,
#   where the skimage.feature.hog function's args and kwargs are obtained and
#   used to wrap that function as an object, so the param config is easily
#   paired with the function. This class wrapping a function is a potential
#   auto-generative or metaprogramming feature of this package.
class HOG(FeatureExtractor):
    """Histogram of Oriented Gradients feature extractor from images.

    Attributes
    ----------
    See `skimage.feature.hog`
    """
    def __init__(
        self,
        means=1,
        concat_mean=False,
        additive=None,
        multiplier=None,
        *args,
        **kwargs,
    ):
        # Save this class' specific attribs first
        self.means = means
        self.concat_mean = concat_mean
        self.additive = additive
        self.multiplier = multiplier

        # Get the args of skimage.feature.hog
        argspec = getargspec(hog)

        # NOTE atm `skimage.feature.hog` is all positional args.
        #if argspec.defaults is not None:
        #    num_required = len(argspec.args) - len(argspec.defaults)
        #else:
        #    num_required = len(argspec.args)
        num_required = 0
        del argspec.args[0]

        on_kwargs = len(args) == 0

        for i, arg in enumerate(argspec.args):
            if i < num_required:
                # Set the arg to required positional value (no default).
                if not on_kwargs and i < len(args):
                    setattr(self, arg, args[i])
                    on_kwargs = i == len(args) - 1
                else:
                    # allow for kwargs to fill in the
                    setattr(self, arg, kwargs[arg])
                    on_kwargs = True
            else:
                # If defaults exist, set them if no positional arg given.
                if not on_kwargs and i < len(args):
                    setattr(self, arg, args[i])
                elif arg in kwargs:
                    setattr(self, arg, kwargs[arg])
                    on_kwargs = True
                else:
                    setattr(self, arg, argspec.defaults[i - num_required])

# TODO decorator for optional type checking funcitonality

# TODO function to generate docs from current args and kwargs in given style
# TODO decorator to check the docs to match current args and kwargs.
#   TODO optionally, correcting them w/ overriding, but defaults to alert user.
