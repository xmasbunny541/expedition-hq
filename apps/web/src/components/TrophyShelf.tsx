import type { Artifact, Milestone } from "../types";

export function TrophyShelf({
  milestones,
  artifacts
}: {
  milestones: Milestone[];
  artifacts: Artifact[];
}) {
  return (
    <section className="living-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Progress</p>
          <h2>Trophy Shelf</h2>
        </div>
        <span className="section-note">Milestones are badges during Season 0.x; XP comes from active time and multipliers.</span>
      </div>
      <div className="trophy-shelf">
        {milestones.map((milestone) => (
          <article className={`trophy trophy-${milestone.status}`} key={milestone.id}>
            <span>{milestone.status}</span>
            <h3>{milestone.name}</h3>
            <p>{milestone.description}</p>
            <strong>{milestone.xp_reward > 0 ? `${milestone.xp_reward} bonus XP` : "badge only"}</strong>
          </article>
        ))}
        {artifacts.map((artifact) => (
          <article className="trophy trophy-artifact" key={artifact.id}>
            <span>{artifact.artifact_type}</span>
            <h3>{artifact.title}</h3>
            <p>{artifact.summary}</p>
            <strong>artifact</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
