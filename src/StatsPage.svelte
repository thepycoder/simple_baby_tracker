<script>
  import StatsBar from "./StatsBar.svelte";
  import { onMount } from "svelte";
  import {
    collection,
    onSnapshot,
    query,
    where,
    getDocs,
    orderBy,
  } from "firebase/firestore";
  import { db, db_table } from "./firebase";
  import { formatTime } from "./utils";

  let activeHours = [];

  function getTotalActiveHours() {
    const now = new Date();
    const sevenDaysAgoMidnight = new Date(
      now.getTime() - 7 * 24 * 60 * 60 * 1000
    );
    sevenDaysAgoMidnight.setHours(0, 0, 0, 0);
    let dateToTypeToDuration = new Map();

    const q = query(
      collection(db, db_table),
      where("start", ">=", sevenDaysAgoMidnight),
      orderBy("start", "desc")
    );

    // We'll use a promise to handle the async nature of the onSnapshot function
    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        snapshot.docs.forEach((doc) => {
          const data = doc.data();
          if (!data.end) {
            return;
          }
          let startDate = data.start.toDate();
          let endDate = data.end.toDate();

          const nextMidnight = new Date(startDate);
          nextMidnight.setDate(nextMidnight.getDate() + 1);
          nextMidnight.setHours(0, 0, 0, 0);

          if (nextMidnight < endDate) {
            updateMap(dateToTypeToDuration, data.type, startDate, nextMidnight);
            updateMap(dateToTypeToDuration, data.type, nextMidnight, endDate);
          } else {
            updateMap(dateToTypeToDuration, data.type, startDate, endDate);
          }
        });

        // Convert map to array
        const resultArray = Array.from(
          dateToTypeToDuration,
          ([date, data]) => ({
            date,
            ...data,
          })
        );

        console.log("Activities Array: ", resultArray);
        activeHours = resultArray;
      },
      (error) => {
        console.error("Error fetching data: ", error);
        reject(error); // Reject the promise in case of error
      }
    );
  }

  function updateMap(dateToTypeToDuration, type, startDate, currentEndDate) {
    const duration = currentEndDate - startDate;
    const dateKey = startDate.toISOString().split("T")[0];

    if (!dateToTypeToDuration.has(dateKey)) {
      dateToTypeToDuration.set(dateKey, {
        [type]: duration,
        [type + "Count"]: 1,
      });
    } else {
      const dateData = dateToTypeToDuration.get(dateKey);
      dateData[type] = (dateData[type] || 0) + duration;
      dateData[type + "Count"] = (dateData[type + "Count"] || 0) + 1;
      dateToTypeToDuration.set(dateKey, dateData); // Update the map entry
    }
  }

  onMount(() => {
    // let tempCounts = [];
    // for (let i = 0; i < 7; i++) {
    //   const { start, end } = getTimestampRangeForDay(i);
    //   const foodStats = await getItemStatsForDayAndType(start, end, "food");
    //   const sleepStats = await getItemStatsForDayAndType(start, end, "sleep");
    //   tempCounts.push({
    //     day: start.toDateString(),
    //     foodCount: foodStats.itemCount,
    //     foodDuration: foodStats.totalDuration,
    //     sleepCount: sleepStats.itemCount,
    //     sleepDuration: sleepStats.totalDuration,
    //   });
    // }
    // console.log(tempCounts);
    // counts.set(tempCounts);

    getTotalActiveHours();
    // const array = Array.from(counts, ([key, value]) => ({
    //   key, // Spread the key
    //   ...value, // Spread the values from the object
    // }));

    // console.log("counts", counts);
  });
</script>

<div class="container">
  <div class="row mb-2 mt-4 justify-content-center">
    <StatsBar />
  </div>
  {#each activeHours as count}
    <div class="row mb-2 justify-content-center">
      <div class="col-md-6 text-center">
        <div class="card">
          <h5 class="card-header">{count.date}</h5>
          <div class="card-body row">
            <div class="col-6 text-center border-end">
              <h1 class="d-inline">{count.foodCount}</h1>
              <small> Voedingen</small>
              <br />
              <span class="text-muted"
                >{formatTime(count.food).slice(0, -3)} in totaal</span
              >
            </div>
            <div class="col-6 text-center">
              <h1 class="d-inline">{count.sleepCount}</h1>
              <small> Slaapjes</small>
              <br />
              <span class="text-muted"
                >{formatTime(count.sleep).slice(0, -3)} in totaal</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
