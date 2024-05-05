<script>
  import StatsBar from "./StatsBar.svelte";
  import { onMount } from "svelte";
  import { collection, query, where, getDocs } from "firebase/firestore";
  import { db, db_table } from "./firebase"; // Assume you have configured firebase
  import { writable } from "svelte/store";

  function getTimestampRangeForDay(dayOffset) {
    const today = new Date();
    const dayStart = new Date(today);
    dayStart.setHours(0, 0, 0, 0);
    dayStart.setDate(today.getDate() - dayOffset);

    const dayEnd = new Date(dayStart);
    dayEnd.setHours(23, 59, 59, 999);

    return {
      start: dayStart,
      end: dayEnd,
    };
  }

  async function countItemsForDayAndType(start, end, type) {
    const itemsQuery = query(
      collection(db, db_table),
      where("end", ">=", start),
      where("end", "<=", end),
      where("type", "==", type)
    );

    const snapshot = await getDocs(itemsQuery);
    return snapshot.size;
  }

  let counts = writable([]);

  onMount(async () => {
    let tempCounts = [];
    for (let i = 0; i < 7; i++) {
      const { start, end } = getTimestampRangeForDay(i);
      const foodCount = await countItemsForDayAndType(start, end, "food");
      const sleepCount = await countItemsForDayAndType(start, end, "sleep");
      tempCounts.push({ day: start.toDateString(), foodCount, sleepCount });
    }
    console.log(tempCounts);
    counts.set(tempCounts);
  });
</script>

<div class="container">
  <div class="row mb-2 justify-content-center">
    <StatsBar />
  </div>
  {#each $counts as count}
    <div class="row mb-2 justify-content-center">
      <div class="col-md-6 text-center">
        <div class="card">
          <h5 class="card-header">{count.day}</h5>
          <div class="card-body row">
            <div class="col-md-6 text-center border-end">
              <h1 class="d-inline">{count.foodCount}</h1>
              <small> Voedingen</small>
              <br />
              <span class="text-muted">xxx in totaal</span>
            </div>
            <div class="col-md-6 text-center">
              <h1 class="d-inline">{count.sleepCount}</h1>
              <small> Slaapjes</small>
              <br />
              <span class="text-muted">xxx in totaal</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
