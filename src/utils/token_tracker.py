class TokenUsageTracker:
    def __init__(self):
        self.usage_log = []

    def log_usage(self, function_name, usage_data):
        """
        Logs token usage for a specific function call.
        """
        entry = {
            "function": function_name,
            "prompt_tokens": usage_data.prompt_tokens,
            "completion_tokens": usage_data.completion_tokens,
            "total_tokens": usage_data.total_tokens,
        }
        self.usage_log.append(entry)

    def display_usage_summary(self):
        """
        Prints a breakdown of token usage across function calls.
        """
        print("\n📊 **Token Usage Breakdown**:")
        total_cost = 0
        for entry in self.usage_log:
            cost = entry["total_tokens"]
            total_cost += cost
            print(f"- {entry['function']}: {cost} tokens "
                  f"(Prompt: {entry['prompt_tokens']}, Completion: {entry['completion_tokens']})")

        print(f"🔹 **Total Tokens Used:** {total_cost}\n")

    def get_total_usage(self):
        """
        Returns the total number of tokens used.
        """
        return sum(entry["total_tokens"] for entry in self.usage_log)

    def reset_log(self):
        """
        Clears the token usage log.
        """
        self.usage_log = []
