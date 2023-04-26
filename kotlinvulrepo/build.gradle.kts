plugins {
    kotlin("multiplatform") version "1.6.0"
}

repositories {
    mavenCentral()
}

kotlin {
  //macosX64("native") { // on macOS
  linuxX64("native") // on Linux
  // mingwX64("native") // on Windows
    binaries {
      executable()
    }
}

tasks.withType<Wrapper> {
  gradleVersion = "4.4.1"
  distributionType = Wrapper.DistributionType.BIN
}
