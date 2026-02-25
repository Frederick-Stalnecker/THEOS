#!/usr/bin/env python3
"""
THEOS Benchmark Suite
=====================

Comprehensive benchmarking framework to validate THEOS performance claims:
- Energy efficiency (50-65% reduction)
- Reasoning quality (convergence, coherence)
- Cache performance (hit rates, speedup)
- Scalability (across models and batch sizes)

Usage:
    python benchmark_suite.py --model gpt2 --output results/
    python benchmark_suite.py --model distilgpt2 --quick-test
    python benchmark_suite.py --help

Results are saved as JSON for analysis with analyze_results.py
"""

import argparse
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Try to import required packages
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install transformers torch")
    sys.exit(1)

# Import THEOS
try:
    from theos import THEOSWrapper, THEOSConfig
except ImportError:
    print("ERROR: THEOS not found in Python path.")
    print("Please run from theos-plugin directory or install with: pip install -e .")
    sys.exit(1)


class BenchmarkSuite:
    """Comprehensive benchmarking suite for THEOS."""
    
    def __init__(self, model_name: str, output_dir: str = "benchmark_results"):
        """
        Initialize benchmark suite.
        
        Args:
            model_name: HuggingFace model name (e.g., "gpt2", "distilgpt2")
            output_dir: Directory to save results
        """
        self.model_name = model_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Loading model: {model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"Model loaded successfully")
        
        # Test prompts covering different reasoning types
        self.test_prompts = [
            # Philosophical reasoning
            "What is the nature of consciousness?",
            "Explain the relationship between free will and determinism.",
            "What is the meaning of existence?",
            
            # Logical reasoning
            "If all humans are mortal, and Socrates is human, what can we conclude?",
            "Explain the difference between correlation and causation.",
            "What is the paradox of the heap?",
            
            # Creative reasoning
            "Describe a world where time flows backwards.",
            "What would happen if gravity suddenly reversed?",
            "Imagine a society without language.",
            
            # Analytical reasoning
            "Compare and contrast democracy and autocracy.",
            "What are the main causes of climate change?",
            "Explain the concept of emergence in complex systems.",
        ]
        
        self.results = {
            "metadata": {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "python_version": sys.version,
                "torch_version": torch.__version__,
            },
            "benchmarks": []
        }
    
    def benchmark_baseline(self, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        """
        Benchmark standard transformer inference (baseline).
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with timing and output data
        """
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        
        end_time = time.time()
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "method": "baseline",
            "prompt": prompt,
            "output": generated_text,
            "time_elapsed": end_time - start_time,
            "tokens_generated": len(outputs[0]) - len(inputs.input_ids[0]),
            "total_tokens": len(outputs[0]),
        }
    
    def benchmark_theos(
        self, 
        prompt: str, 
        config: Optional[THEOSConfig] = None
    ) -> Dict[str, Any]:
        """
        Benchmark THEOS inference.
        
        Args:
            prompt: Input prompt
            config: THEOS configuration (uses default if None)
            
        Returns:
            Dictionary with timing, cycle, and output data
        """
        if config is None:
            config = THEOSConfig(max_cycles=5, max_tokens=50)
        
        theos = THEOSWrapper(self.model, self.tokenizer, config=config)
        
        start_time = time.time()
        response = theos.generate(prompt, return_metadata=True)
        end_time = time.time()
        
        # Get cache stats
        cache_stats = theos.get_cache_stats()
        
        return {
            "method": "theos",
            "prompt": prompt,
            "output": response.text,
            "time_elapsed": end_time - start_time,
            "cycles": response.cycles,
            "converged": response.converged,
            "tokens_used": response.tokens_used,
            "cached": response.cached,
            "cache_stats": cache_stats,
            "governor_scores": response.governor_scores,
        }
    
    def benchmark_cache_performance(self, prompts: List[str]) -> Dict[str, Any]:
        """
        Benchmark cache hit rates and speedup.
        
        Args:
            prompts: List of prompts (will be run twice to test caching)
            
        Returns:
            Dictionary with cache performance metrics
        """
        config = THEOSConfig(max_cycles=5, max_tokens=50, enable_cache=True)
        theos = THEOSWrapper(self.model, self.tokenizer, config=config)
        
        # First run - populate cache
        first_run_times = []
        for prompt in prompts:
            start = time.time()
            theos.generate(prompt)
            first_run_times.append(time.time() - start)
        
        # Second run - should hit cache
        second_run_times = []
        cache_hits = 0
        for prompt in prompts:
            start = time.time()
            response = theos.generate(prompt, return_metadata=True)
            second_run_times.append(time.time() - start)
            if response.cached:
                cache_hits += 1
        
        cache_stats = theos.get_cache_stats()
        
        avg_first = sum(first_run_times) / len(first_run_times)
        avg_second = sum(second_run_times) / len(second_run_times)
        speedup = avg_first / avg_second if avg_second > 0 else 0
        
        return {
            "test": "cache_performance",
            "num_prompts": len(prompts),
            "cache_hits": cache_hits,
            "hit_rate": cache_hits / len(prompts),
            "avg_first_run_time": avg_first,
            "avg_second_run_time": avg_second,
            "speedup_factor": speedup,
            "cache_stats": cache_stats,
        }
    
    def benchmark_convergence(self, prompts: List[str]) -> Dict[str, Any]:
        """
        Benchmark convergence behavior across different cycle limits.
        
        Args:
            prompts: List of test prompts
            
        Returns:
            Dictionary with convergence statistics
        """
        cycle_limits = [3, 5, 7, 10]
        results = []
        
        for max_cycles in cycle_limits:
            config = THEOSConfig(max_cycles=max_cycles, max_tokens=50)
            theos = THEOSWrapper(self.model, self.tokenizer, config=config)
            
            converged_count = 0
            avg_cycles = 0
            
            for prompt in prompts:
                response = theos.generate(prompt, return_metadata=True)
                if response.converged:
                    converged_count += 1
                avg_cycles += response.cycles
            
            avg_cycles /= len(prompts)
            
            results.append({
                "max_cycles": max_cycles,
                "convergence_rate": converged_count / len(prompts),
                "avg_cycles_used": avg_cycles,
            })
        
        return {
            "test": "convergence_analysis",
            "num_prompts": len(prompts),
            "results": results,
        }
    
    def benchmark_energy_efficiency(self, prompts: List[str]) -> Dict[str, Any]:
        """
        Benchmark computational efficiency (proxy for energy).
        
        Measures:
        - Total tokens generated
        - Inference time
        - Tokens per second
        
        Args:
            prompts: List of test prompts
            
        Returns:
            Dictionary comparing baseline vs THEOS efficiency
        """
        # Baseline measurements
        baseline_total_time = 0
        baseline_total_tokens = 0
        
        for prompt in prompts:
            result = self.benchmark_baseline(prompt, max_tokens=50)
            baseline_total_time += result["time_elapsed"]
            baseline_total_tokens += result["tokens_generated"]
        
        # THEOS measurements
        config = THEOSConfig(max_cycles=5, max_tokens=50)
        theos = THEOSWrapper(self.model, self.tokenizer, config=config)
        
        theos_total_time = 0
        theos_total_tokens = 0
        theos_total_cycles = 0
        
        for prompt in prompts:
            start = time.time()
            response = theos.generate(prompt, return_metadata=True)
            theos_total_time += time.time() - start
            theos_total_tokens += response.tokens_used
            theos_total_cycles += response.cycles
        
        # Calculate efficiency metrics
        baseline_tokens_per_sec = baseline_total_tokens / baseline_total_time
        theos_tokens_per_sec = theos_total_tokens / theos_total_time
        
        time_reduction = (baseline_total_time - theos_total_time) / baseline_total_time
        token_reduction = (baseline_total_tokens - theos_total_tokens) / baseline_total_tokens
        
        return {
            "test": "energy_efficiency",
            "num_prompts": len(prompts),
            "baseline": {
                "total_time": baseline_total_time,
                "total_tokens": baseline_total_tokens,
                "tokens_per_second": baseline_tokens_per_sec,
            },
            "theos": {
                "total_time": theos_total_time,
                "total_tokens": theos_total_tokens,
                "total_cycles": theos_total_cycles,
                "avg_cycles_per_prompt": theos_total_cycles / len(prompts),
                "tokens_per_second": theos_tokens_per_sec,
            },
            "comparison": {
                "time_reduction_percent": time_reduction * 100,
                "token_reduction_percent": token_reduction * 100,
                "efficiency_gain": (1 - theos_total_time / baseline_total_time) * 100,
            }
        }
    
    def run_full_benchmark(self, quick_test: bool = False):
        """
        Run complete benchmark suite.
        
        Args:
            quick_test: If True, use subset of prompts for faster testing
        """
        print("=" * 70)
        print("THEOS BENCHMARK SUITE")
        print("=" * 70)
        print(f"Model: {self.model_name}")
        print(f"Mode: {'Quick Test' if quick_test else 'Full Benchmark'}")
        print()
        
        # Use subset for quick test
        prompts = self.test_prompts[:3] if quick_test else self.test_prompts
        
        # 1. Energy Efficiency Benchmark
        print("Running energy efficiency benchmark...")
        try:
            efficiency_results = self.benchmark_energy_efficiency(prompts)
            self.results["benchmarks"].append(efficiency_results)
            print(f"✓ Time reduction: {efficiency_results['comparison']['time_reduction_percent']:.1f}%")
            print(f"✓ Token reduction: {efficiency_results['comparison']['token_reduction_percent']:.1f}%")
        except Exception as e:
            print(f"✗ Energy efficiency benchmark failed: {e}")
            traceback.print_exc()
        
        print()
        
        # 2. Cache Performance Benchmark
        print("Running cache performance benchmark...")
        try:
            cache_results = self.benchmark_cache_performance(prompts)
            self.results["benchmarks"].append(cache_results)
            print(f"✓ Cache hit rate: {cache_results['hit_rate']:.1%}")
            print(f"✓ Speedup factor: {cache_results['speedup_factor']:.2f}x")
        except Exception as e:
            print(f"✗ Cache performance benchmark failed: {e}")
            traceback.print_exc()
        
        print()
        
        # 3. Convergence Analysis
        print("Running convergence analysis...")
        try:
            convergence_results = self.benchmark_convergence(prompts)
            self.results["benchmarks"].append(convergence_results)
            for result in convergence_results["results"]:
                print(f"✓ Max cycles {result['max_cycles']}: "
                      f"{result['convergence_rate']:.1%} convergence, "
                      f"{result['avg_cycles_used']:.1f} avg cycles")
        except Exception as e:
            print(f"✗ Convergence analysis failed: {e}")
            traceback.print_exc()
        
        print()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir, 
            f"benchmark_{self.model_name}_{timestamp}.json"
        )
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("=" * 70)
        print(f"✅ Benchmark complete!")
        print(f"Results saved to: {output_file}")
        print("=" * 70)
        print()
        print("Next step: Run analyze_results.py to generate visualizations and report")


def main():
    parser = argparse.ArgumentParser(
        description="THEOS Benchmark Suite - Validate performance claims"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="distilgpt2",
        help="HuggingFace model name (default: distilgpt2)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results",
        help="Output directory for results (default: benchmark_results)"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with subset of prompts"
    )
    
    args = parser.parse_args()
    
    try:
        suite = BenchmarkSuite(args.model, args.output)
        suite.run_full_benchmark(quick_test=args.quick_test)
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nBenchmark failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
