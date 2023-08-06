#include <gtest/gtest.h>
#include <glog/logging.h>
int main(int argc, char* argv[]) {
  google::InstallFailureSignalHandler();
  testing::InitGoogleTest(&argc, argv);
  int rc = RUN_ALL_TESTS();
  exit(rc);
}
