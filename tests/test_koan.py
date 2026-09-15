"""Tests for the _fill_ sentinel and Koan base class."""
import pytest
from llmsquire.koan import Koan, _fill_, FillMeInError


class TestFillSentinel:
    """The _fill_ sentinel must fail comparisons clearly."""

    def test_fill_is_not_equal_to_anything(self):
        assert (_fill_ == "hello") is False
        assert (_fill_ == 42) is False
        assert (_fill_ == None) is False
        assert (_fill_ == True) is False
        assert (_fill_ == _fill_) is False  # even itself

    def test_fill_is_not_equal_using_ne(self):
        assert (_fill_ != "hello") is True
        assert (_fill_ != 42) is True

    def test_fill_repr_is_descriptive(self):
        assert repr(_fill_) == "_fill_"

    def test_fill_bool_is_false(self):
        assert bool(_fill_) is False

    def test_fill_assertion_fails(self):
        # assert _fill_ == True produces an AssertionError because
        # _fill_.__eq__ returns False. The helpful FillMeInError is
        # raised by the Koan assertion helpers, not by bare assert.
        with pytest.raises(AssertionError):
            assert _fill_ == True


class TestKoanBaseClass:
    """The Koan base class provides per-test llm and assertions."""

    def test_koan_has_llm_instance(self):
        class MyKoan(Koan):
            def test_dummy(self):
                pass

        k = MyKoan("test_dummy")
        k.setup()
        assert k.llm is not None
        assert hasattr(k.llm, 'ask')
        assert hasattr(k.llm, 'converse')
        assert hasattr(k.llm, 'trace')

    def test_koan_has_fill_in_namespace(self):
        class MyKoan(Koan):
            def test_dummy(self):
                pass

        k = MyKoan("test_dummy")
        k.setup()
        # _fill_ should be accessible from the instance
        assert k._fill_ is not None

    def test_koan_trace_is_fresh_per_test(self):
        class MyKoan(Koan):
            def test_first(self):
                pass
            def test_second(self):
                pass

        k1 = MyKoan("test_first")
        k1.setup()
        trace1_id = id(k1.llm.trace)

        k2 = MyKoan("test_second")
        k2.setup()
        trace2_id = id(k2.llm.trace)

        assert trace1_id != trace2_id

    def test_koan_assert_match_passes_on_substring(self):
        class MyKoan(Koan):
            def test_dummy(self):
                pass

        k = MyKoan("test_dummy")
        k.setup()
        k.assert_match("hello", "hello world")  # should not raise

    def test_koan_assert_match_fails_on_no_match(self):
        class MyKoan(Koan):
            def test_dummy(self):
                pass

        k = MyKoan("test_dummy")
        k.setup()
        with pytest.raises(AssertionError, match="xyzzy"):
            k.assert_match("xyzzy", "hello world")

    def test_koan_assert_match_fails_with_fill_me_in_message(self):
        class MyKoan(Koan):
            def test_dummy(self):
                pass

        k = MyKoan("test_dummy")
        k.setup()
        with pytest.raises(FillMeInError, match="_fill_"):
            k.assert_match(k._fill_, "hello world")