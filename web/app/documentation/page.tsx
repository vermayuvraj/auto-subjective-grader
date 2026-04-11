import { redirect } from "next/navigation";
import { DOCUMENTATION_HREF } from "../../lib/documentation";

export const metadata = {
  title: "Documentation | Ai Grader",
  description:
    "Documentation for Ai Grader, an AI-powered subjective grading tool for educators. Learn how to use Ai Grader to create rubrics, grade assignments, and provide feedback to students efficiently.",
};

export default function DocumentationPage() {
  redirect(DOCUMENTATION_HREF);
}
