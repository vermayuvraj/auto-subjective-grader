import { SectionShell } from "../../components/section-shell";
import { fetchJson } from "../../lib/api";
import { fallbackResources } from "../../lib/fallback-data";

type ResourceItem = {
  category: string;
  name: string;
  purpose: string;
};

export default async function ResourcesPage() {
  const resources = await fetchJson<ResourceItem[]>("/api/resources", fallbackResources);

  return (
    <SectionShell
      title="Resources"
      subtitle="Core libraries, models, frameworks, and backend services currently used in the platform."
    >
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Name</th>
              <th>Purpose</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((item) => (
              <tr key={`${item.category}-${item.name}`}>
                <td>{item.category}</td>
                <td>{item.name}</td>
                <td>{item.purpose}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionShell>
  );
}
