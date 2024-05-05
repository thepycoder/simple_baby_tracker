<script>
  import StatsBar from "./StatsBar.svelte";
  import { onMount } from "svelte";
  import { collection, query, where, getDocs } from "firebase/firestore";
  import { db, db_table } from "./firebase";
  import { writable } from "svelte/store";
  import { formatTime } from "./utils";

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

  async function getItemStatsForDayAndType(start, end, type) {
    const itemsQuery = query(
      collection(db, db_table),
      where("end", ">=", start),
      where("end", "<=", end),
      where("type", "==", type)
    );

    const snapshot = await getDocs(itemsQuery);
    let itemCount = 0;
    let totalDuration = 0;

    snapshot.forEach((doc) => {
      const data = doc.data();
      itemCount++;
      if (data.start && data.end) {
        totalDuration +=
          data.end.toDate().getTime() - data.start.toDate().getTime();
      }
    });

    return { itemCount, totalDuration };
  }

  let counts = writable([]);

  onMount(async () => {
    let tempCounts = [];
    for (let i = 0; i < 7; i++) {
      const { start, end } = getTimestampRangeForDay(i);
      const foodStats = await getItemStatsForDayAndType(start, end, "food");
      const sleepStats = await getItemStatsForDayAndType(start, end, "sleep");
      tempCounts.push({
        day: start.toDateString(),
        foodCount: foodStats.itemCount,
        foodDuration: foodStats.totalDuration,
        sleepCount: sleepStats.itemCount,
        sleepDuration: sleepStats.totalDuration,
      });
    }
    console.log(tempCounts);
    counts.set(tempCounts);
  });
</script>

<div class="container">
  <div class="row mb-2 mt-4 justify-content-center">
    <StatsBar />
  </div>
  {#each $counts as count}
    <div class="row mb-2 justify-content-center">
      <div class="col-md-6 text-center">
        <div class="card">
          <h5 class="card-header">{count.day}</h5>
          <div class="card-body row">
            <div class="col-6 text-center border-end">
              <h1 class="d-inline">{count.foodCount}</h1>
              <small> Voedingen</small>
              <br />
              <span class="text-muted"
                >{formatTime(count.foodDuration)} in totaal</span
              >
            </div>
            <div class="col-6 text-center">
              <h1 class="d-inline">{count.sleepCount}</h1>
              <small> Slaapjes</small>
              <br />
              <span class="text-muted"
                >{formatTime(count.sleepDuration)} in totaal</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
