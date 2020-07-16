import asyncio
import contextlib
import enum
import io
import logging
import re
import textwrap
import traceback
import typing as t
from datetime import datetime

from discord.ext import commands

from bot.bot import Ryan
from bot.constants import Users
from bot.utils import msg_error, msg_success

log = logging.getLogger(__name__)

CODEBLOCK_REGEX = re.compile(r"(^```(py(thon)?)?\n)|(```$)")
INDENT_DEPTH = 4

T_MAX = 30  # Seconds to wait before exec job finishes, raise timeout otherwise

# To allow execution of coroutines, we'll inject the code into this template, which
# wraps everything in an awaitable body, prepares the coroutine, and assigns it
ASYNC_WRAP = """
async def wrap():
{in_code}

coro = wrap()
"""


class ExitCode(enum.Enum):
    """Flags signaling outcome when executing code."""

    SUCCESS = 0
    FAIL_COMPILE = 1
    FAIL_RUNTIME = 2
    FAIL_TIMEOUT = 3


def error_message(exc: Exception) -> str:
    """
    Turn `exc` into a pretty, succinct error message.

    This only wraps the `traceback` module - sadly its interface is fairly ugly
    and so we can help ourselves by at least abstracting the ugly away.

    The message does not contain the stack trace, as it's generally not necessary
    and brings about a certain level of complexity.
    """
    error_lines = ["[Traceback ignored]\n\n"] + traceback.format_exception_only(type(exc), exc)
    return "".join(error_lines)


async def run_code(in_text: str, in_locals: t.Dict[str, t.Any]) -> t.Tuple[ExitCode, str]:
    """
    Attempt to extract Python code from `in_text` Markdown codeblock, compile & execute it.

    At runtime, the executed codeblock will be given access to `in_locals`, which means that
    any kind of surrounding context can be passed in. Be careful with this!

    If no locals are to be used, pass an empty mapping.

    The return type is an ExitCode member flag signaling the outcome, and an optional message.

    We redirect & capture stdout at runtime, however, the executed code may not ever write to
    stdout, in which case the second return value is simply an empty string. In the case of
    a runtime exception, we return a formatted error message instead of stdout.

    The task is killed after `T_MAX` seconds if it doesn't finish by then. The limit isn't strict
    and is mostly in place to prevent an accidental endless loop, which we would otherwise have
    no way to cancel once it gets awaited.
    """
    log.debug(f"Processing received text: {in_text!r}")  # Force repr due to new lines polluting logfile
    extracted_code = CODEBLOCK_REGEX.sub("", in_text.strip())

    log.debug(f"Indenting code by {INDENT_DEPTH} spaces to allow async wrap")
    wrapped_code = ASYNC_WRAP.format(in_code=textwrap.indent(extracted_code, prefix=" " * INDENT_DEPTH))

    log.debug(f"Attempting to compile: {wrapped_code!r}")
    try:
        compiled_code = compile(wrapped_code, filename="<memory>", mode="exec")

    # We'll abort & exit early if the code fails to compile, propagating the error message,
    # which is generally pretty useful as it shows where the parser failed
    except Exception as compile_exc:
        log.debug(f"Failed to compile: {compile_exc}")
        return ExitCode.FAIL_COMPILE, error_message(compile_exc)

    log.debug("Compiled successfully, executing...")
    out_feed = io.StringIO()

    # Attempt to execute our compiled code and capture stdout into `out_feed`
    try:
        with contextlib.redirect_stdout(out_feed):
            exec(compiled_code, in_locals)
            await asyncio.wait_for(in_locals["coro"], timeout=T_MAX)

    # We consider timeouts to be a special case with its own exit code, the exception
    # raised by asyncio doesn't include `T_MAX` so we use our own message
    except asyncio.TimeoutError as timeout_exc:
        log.debug(f"Schedule task timed out: {timeout_exc} ({T_MAX=})")
        return ExitCode.FAIL_TIMEOUT, f"Timeout: task killed after {T_MAX} seconds"

    # If anything else goes wrong, we'll propagate the error message as a string
    except Exception as runtime_exc:
        log.debug(f"Code failed at runtime: {runtime_exc}")
        return ExitCode.FAIL_RUNTIME, error_message(runtime_exc)

    # Otherwise, we'll retrieve stdout from our feed and return it - note that
    # we do not expose stdout if something failed, which means that a runtime
    # exception will hide "override" it, which is probably ok for now
    else:
        log.debug("Code executed successfully!")
        return ExitCode.SUCCESS, out_feed.getvalue() or "[No output]"


class Execute(commands.Cog):
    """
    Support for code injection & evaluation at runtime.

    This cog allows execution of arbitrary code at the host machine with no sand-boxing
    in place. Clearly this is super dangerous, and only trusted users should be given
    invocation rights.
    """

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context) -> bool:
        """Permit only a specific user id to operate the extension."""
        return ctx.author.id == Users.kwzrd

    @commands.command("execute", aliases=["exec"])
    async def execute(self, ctx: commands.Context, *, raw_code: str) -> None:
        """
        Attempt to compile & execute `raw_code` and expose stdout.

        This method merely passes `raw_code`, unprocessed, to `run_code`. Once the coroutine
        finishes, we prepare a pretty response embed and return it to `ctx`.
        """
        start_time = datetime.now()

        async with ctx.typing():
            exit_code, out_message = await run_code(raw_code, locals())

        time_diff = (datetime.now() - start_time).total_seconds()
        response = (
            f"Finished with: `{exit_code} | {time_diff} secs`\n"
            f"```\n{out_message}```"  # Newline necessary to avoid markdown codeblock lang definition
        )
        make_embed = msg_success if exit_code is ExitCode.SUCCESS else msg_error
        await ctx.send(embed=make_embed(response))


def setup(bot: Ryan) -> None:
    """Load the Execute cog."""
    bot.add_cog(Execute(bot))
