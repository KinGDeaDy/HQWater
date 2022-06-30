console.log("Script started");
Java.perform(function x() {
  Java.choose("com.google.firebase.iid.FirebaseInstanceId", {
    onMatch: function (instance) {
      console.log("Found instance: " + instance);
      console.log(instance.b());
      send(instance.b());
    },
    onComplete: function () {},
  });
});
