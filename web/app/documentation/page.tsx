import { redirect } from "next/navigation";
import { DOCUMENTATION_HREF } from "../../lib/documentation";

export const metadata = {
  title: "Documentation | Ai Grader",
  description:
    "Standalone project report for the Automated Subjective Answer Sheet Evaluation System.",
};

export default function DocumentationPage() {
  redirect(DOCUMENTATION_HREF);
}
