class TokenUsageTracker:
    def __init__(self):
        self.usage_log = []

    def log_usage(self, function_name, usage_data):
        """Logs token usage for a specific function call."""
        entry = {
            "function": function_name,
            "prompt_tokens": usage_data.prompt_tokens,
            "completion_tokens": usage_data.completion_tokens,
            "total_tokens": usage_data.total_tokens,
        }
        self.usage_log.append(entry)

    def display_usage_summary(self):
        """Prints a clean breakdown with smart grouping."""
        print("\n📊 **Token Usage Breakdown**:")
        
        # Auto-group related functions
        categories = {
            "Feedback Analysis": ["feedback", "correction"],
            "Memory Operations": ["memory", "summary"],
            "Response Generation": ["response", "generate"]
        }
        
        totals = {"Prompt": 0, "Completion": 0, "Total": 0}
        
        for category, keywords in categories.items():
            cat_tokens = {
                "Prompt": 0,
                "Completion": 0,
                "Total": 0
            }
            
            for entry in self.usage_log:
                if any(kw in entry["function"].lower() for kw in keywords):
                    cat_tokens["Prompt"] += entry["prompt_tokens"]
                    cat_tokens["Completion"] += entry["completion_tokens"]
                    cat_tokens["Total"] += entry["total_tokens"]
                    
            if cat_tokens["Total"] > 0:
                print(f"- {category}: {cat_tokens['Total']} tokens "
                      f"(P: {cat_tokens['Prompt']}, C: {cat_tokens['Completion']})")
                
            totals["Prompt"] += cat_tokens["Prompt"]
            totals["Completion"] += cat_tokens["Completion"]
            totals["Total"] += cat_tokens["Total"]

        print(f"\n🔹 **Total**: {totals['Total']} tokens "
              f"(Prompt: {totals['Prompt']}, Completion: {totals['Completion']})")

    def get_total_usage(self):
        return sum(entry["total_tokens"] for entry in self.usage_log)

    def reset_log(self):
        self.usage_log = []