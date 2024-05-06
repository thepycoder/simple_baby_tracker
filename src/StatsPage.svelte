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

    const q = query(
      collection(db, db_table),
      where("end", ">=", sevenDaysAgoMidnight),
      orderBy("end", "desc")
    );

    // We'll use a promise to handle the async nature of the onSnapshot function
    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        let dateToTypeToDuration = new Map();
        snapshot.docs.forEach((doc) => {
          const data = doc.data();
          if (!data.end) {
            return;
          }
          if (data.type == "sleep") {
            console.log(data.start.toDate() + " => ", data.end.toDate());
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
        activeHours = resultArray.slice(1, 7);
      },
      (error) => {
        console.error("Error fetching data: ", error);
        reject(error); // Reject the promise in case of error
      }
    );
  }

  function updateMap(dateToTypeToDuration, type, startDate, currentEndDate) {
    const duration = currentEndDate - startDate;
    const dateString = startDate.toLocaleDateString("nl-BE", {
      year: "numeric",
      month: "long",
      day: "numeric",
      weekday: "long",
    });
    const dateKey = dateString.charAt(0).toUpperCase() + dateString.slice(1);

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
    getTotalActiveHours();
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
