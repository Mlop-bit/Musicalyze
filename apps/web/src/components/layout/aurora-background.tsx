import styles from "./aurora-background.module.css";

export function AuroraBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      <div className={styles.aurora}>
        <div className={`${styles.ribbon} ${styles.ribbon1}`} />
        <div className={`${styles.ribbon} ${styles.ribbon2}`} />
        <div className={`${styles.ribbon} ${styles.ribbon3}`} />
      </div>
    </div>
  );
}
