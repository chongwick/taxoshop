"""Command line entry points for the research pipeline."""
import argparse
import sys
from pathlib import Path

from .artifacts import inside, read_json, write_json
from .contracts import validate_catalog, validate_micro
from .dedup import candidates
from .macro import load_reports, run_macro
from .micro import run_micro
from .models import CodexModel, ReplayModel


def model_options(parser):
    parser.add_argument('--model', default='gpt-5.6-terra', help='Codex model identifier; recorded in every run')
    parser.add_argument('--effort', choices=['low', 'medium', 'high', 'xhigh'], default='high')
    parser.add_argument('--responses', type=Path, help='Replay named JSON responses from a directory without calling a model')
    parser.add_argument('--resume', action='store_true', help='Resume only with identical inputs, model, prompts, schemas, and implementation')
    parser.add_argument('--attempts', type=int, default=2)
    parser.add_argument('--max-prompt-chars', type=int, default=750000, help='Fail explicitly if a complete prompt exceeds this limit')


def parser():
    result = argparse.ArgumentParser(description='Evidence-backed CPython bug analysis and pattern induction')
    commands = result.add_subparsers(dest='command', required=True)
    micro = commands.add_parser('micro', help='Fetch evidence and generate comprehensive bug analyses')
    micro.add_argument('--input', type=Path, default=Path('workdir_python/github_issue_links.txt'))
    micro.add_argument('--output', type=Path, required=True)
    micro.add_argument('--evidence-dir', type=Path, help='Import offline evidence bundles instead of fetching GitHub')
    micro.add_argument('--limit', type=int)
    micro.add_argument('--collect-only', action='store_true', help='Archive evidence without calling the model; use --resume to analyze later')
    model_options(micro)
    macro = commands.add_parser('macro', help='Synthesize patterns and an agent search guide')
    macro.add_argument('--input', type=Path, required=True, help='Micro run directory')
    macro.add_argument('--output', type=Path, required=True)
    macro.add_argument('--method', choices=['incremental', 'embedding'], default='incremental')
    macro.add_argument('--seed', type=int, default=0)
    macro.add_argument('--split', type=Path, help='Frozen canonical split; synthesize only the selected partition')
    macro.add_argument('--partition', choices=['discovery', 'development'], default='discovery')
    macro.add_argument('--allow-partial', action='store_true', help='Explicitly use only completed reports from a partial micro run')
    macro.add_argument('--embedding-model', default='sentence-transformers/all-mpnet-base-v2')
    macro.add_argument('--embedding-revision', help='Pinned model commit SHA; required for embedding runs')
    macro.add_argument('--threshold', type=float, default=0.3)
    model_options(macro)
    check = commands.add_parser('validate', help='Validate a micro report or a complete macro catalog')
    check.add_argument('artifact', type=Path)
    check.add_argument('--root', type=Path, required=True, help='Run root for resolving and hashing evidence')
    dedup = commands.add_parser('dedup', help='Export diagnostic duplicate candidates without merging')
    dedup.add_argument('--input', type=Path, required=True)
    dedup.add_argument('--output', type=Path, required=True)
    dedup.add_argument('--allow-partial', action='store_true')
    split = commands.add_parser('split', help='Freeze canonical discovery/development/evaluation partitions')
    split.add_argument('--input', type=Path, required=True, help='Completed micro run')
    split.add_argument('--output', type=Path, required=True)
    split.add_argument('--seed', type=int, default=0)
    split.add_argument('--development', type=float, default=0.2)
    split.add_argument('--evaluation', type=float, default=0.2)
    hunt = commands.add_parser('hunt', help='Investigate a bounded source snapshot for candidate defects')
    hunt.add_argument('--repo', type=Path, required=True)
    hunt.add_argument('--revision', required=True, help='Full target commit SHA')
    hunt.add_argument('--file', action='append', required=True, dest='files', help='Exact repository-relative source file; repeat to add files')
    hunt.add_argument('--output', type=Path, required=True)
    hunt.add_argument('--condition', choices=['none', 'micro', 'incremental', 'embedding'], default='none')
    hunt.add_argument('--input', type=Path, help='Micro or macro run supplying documentation')
    hunt.add_argument('--split', type=Path, help='Required for corpus-derived documentation')
    hunt.add_argument('--partition', choices=['discovery', 'development'], default='discovery')
    hunt.add_argument('--max-source-bytes', type=int, default=500000)
    hunt.add_argument('--max-documentation-chars', type=int, default=100000)
    hunt.add_argument('--max-findings', type=int, default=20)
    hunt.add_argument('--seed', type=int, default=0, help='Recorded repetition label, not a deterministic model seed')
    model_options(hunt)
    review = commands.add_parser('review-template', help='Create an unfilled review form for a completed hunt')
    review.add_argument('--input', type=Path, required=True)
    review.add_argument('--output', type=Path, required=True)
    evaluation = commands.add_parser('evaluate', help='Summarize hunt runs and externally reviewed evidence')
    evaluation.add_argument('--input', type=Path, action='append', required=True, help='Hunt run; repeat for comparisons')
    evaluation.add_argument('--review', type=Path, action='append', default=[], help='Completed review JSON; repeat per reviewed run')
    evaluation.add_argument('--output', type=Path, required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    model = None
    try:
        if args.command in ('micro', 'macro', 'hunt'):
            if args.attempts < 1 or args.max_prompt_chars < 1:
                raise ValueError('attempts and max-prompt-chars must be positive')
            if args.command == 'macro' and args.method == 'embedding' and not args.embedding_revision:
                raise ValueError('--embedding-revision is required for embedding runs')
            model = ReplayModel(args.responses) if args.responses else CodexModel(args.model, args.effort)
            common = dict(resume=args.resume, attempts=args.attempts, max_prompt_chars=args.max_prompt_chars)
            if args.command == 'micro':
                result = run_micro(args.input, args.output, model, evidence_dir=args.evidence_dir, limit=args.limit, collect_only=args.collect_only, **common)
            elif args.command == 'macro':
                result = run_macro(args.input, args.output, model, method=args.method, seed=args.seed,
                                   allow_partial=args.allow_partial, embedding_model=args.embedding_model,
                                   embedding_revision=args.embedding_revision, threshold=args.threshold,
                                   split_path=args.split, partition=args.partition, **common)
            else:
                from .hunt import run_hunt
                result = run_hunt(args.repo, args.revision, args.files, args.output, model,
                                  condition=args.condition, input_dir=args.input, split_path=args.split, partition=args.partition,
                                  max_source_bytes=args.max_source_bytes, max_documentation_chars=args.max_documentation_chars,
                                  max_findings=args.max_findings, seed=args.seed, **common)
            print(f'{result["run_id"]}: {result["status"]} — {args.output}')
            return 0 if result['status'] in ('complete', 'evidence_collected') else 1
        if args.command == 'validate':
            artifact = read_json(args.artifact)
            if 'catalog_id' in artifact:
                reports = [read_json(inside(args.root, item['artifact_path'])) for item in artifact['input_reports']]
                for report in reports:
                    validate_micro(report, args.root / 'inputs')
                validate_catalog(artifact, reports, args.root)
            elif 'hunt_id' in artifact:
                from .hunt import load_hunt
                _, expected = load_hunt(args.root)
                if artifact != expected:
                    raise ValueError('Artifact differs from the canonical hunt report')
            elif 'fractions' in artifact:
                from .evaluation import validate_split
                validate_split(artifact)
            elif 'hunt_report_sha256' in artifact:
                from .evaluation import validate_review
                from .hunt import load_hunt
                manifest, report = load_hunt(args.root)
                validate_review(artifact, report, args.artifact.parent, manifest['report_sha256'])
            else:
                validate_micro(artifact, args.root)
            print('Valid structure, references, and artifact integrity. Causal truth requires review.')
        elif args.command == 'dedup':
            reports = [report for report, _ in load_reports(args.input, args.allow_partial)]
            write_json(args.output, candidates(reports))
            print(f'Wrote duplicate candidates: {args.output}')
        elif args.command == 'split':
            from .evaluation import create_split
            result = create_split(args.input, args.output, seed=args.seed, development=args.development, evaluation=args.evaluation)
            counts = {name: sum(r['partition'] == name for r in result['reports']) for name in ('discovery', 'development', 'evaluation')}
            print(f'Wrote frozen split: {args.output} — {counts}')
        elif args.command == 'review-template':
            from .evaluation import review_template
            review_template(args.input, args.output)
            print(f'Wrote review form: {args.output}. Fill reviewer and decisions; validated findings require execution evidence.')
        elif args.command == 'evaluate':
            from .evaluation import evaluate
            evaluate(args.input, args.output, review_paths=args.review)
            print(f'Wrote descriptive evaluation: {args.output / "summary.json"}')
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    finally:
        if model is not None:
            model.close()
