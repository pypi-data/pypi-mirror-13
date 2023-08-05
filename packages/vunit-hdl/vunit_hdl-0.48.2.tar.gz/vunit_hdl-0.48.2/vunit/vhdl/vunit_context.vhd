-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (c) 2014-2015, Lars Asplund lars.anders.asplund@gmail.com

context vunit_context is
  library vunit_lib;
  use vunit_lib.lang.all;
  use vunit_lib.textio.all;
  use vunit_lib.string_ops.all;
  use vunit_lib.dictionary.all;
  use vunit_lib.path.all;
  use vunit_lib.log_types_pkg.all;
  use vunit_lib.log_special_types_pkg.all;
  use vunit_lib.log_pkg.all;
  use vunit_lib.check_types_pkg.all;
  use vunit_lib.check_special_types_pkg.all;
  use vunit_lib.check_pkg.all;
  use vunit_lib.run_types_pkg.all;
  use vunit_lib.run_special_types_pkg.all;
  use vunit_lib.run_base_pkg.all;
  use vunit_lib.run_pkg.all;
end context;
