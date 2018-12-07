#include <stdlib.h>
#include <unistd.h>
#include "version.h"
#include "doxygen.h"
#include "outputgen.h"
#include "parserintf.h"
#include "classlist.h"
#include "config.h"
#include "filedef.h"
#include "util.h"
#include "filename.h"
#include "arguments.h"
#include "memberlist.h"
#include "types.h"
#include <string>
#include <cstdlib>
#include <sstream>
#include <map>
#include <qcstring.h>
#include <qregexp.h>
#include "namespacedef.h"

static bool is_c_code = true;

static bool checkLanguage(std::string filename, std::string extension) {
  if (filename.find(extension, filename.size() - extension.size()) != std::string::npos) {
    return true;
  } else {
    return false;
  }
}

/* Detects the programming language of the project. Actually, we only care
 * about whether it is a C project or not. */
static void checkProgrammingLanguage(FileNameListIterator& fnli) {
  FileName* fn;
  for (fnli.toFirst(); (fn=fnli.current()); ++fnli) {
    std::string filename = fn->fileName();
    if (
        checkLanguage(filename, ".cc") ||
        checkLanguage(filename, ".cxx") ||
        checkLanguage(filename, ".cpp") ||
        checkLanguage(filename, ".java") ||
        checkLanguage(filename, ".py") ||
        checkLanguage(filename, ".pyw") ||
        checkLanguage(filename, ".cs")
       ) {
      is_c_code = false;
    }
  }
}

static void checkClasses(FileDef *fd) {
    ClassSDict *classes = fd->getClassSDict();
    ClassDef *cd;
    if (classes) {
          ClassSDict::Iterator cli(*classes);
          for (cli.toFirst(); (cd = cli.current()); ++cli) {
            if (!cd->visited) {
              classInformation(cd);
              cd->visited=TRUE;
            }
            else {
              cd->visited=FALSE;
            }
          }
        }
}

static bool checkOverrideArg(ArgumentList *argList, MemberDef *md) {
  ArgumentListIterator iterator(*argList);
  Argument * argument = iterator.toFirst();

  if(!md->isFunction() || argList->count() == 0){
      return false;
  }

  if(argument != NULL) {
    for(; (argument = iterator.current()); ++iterator){
        if(md->name() == argument->name) {
            return true;
        }
    }
  }

  return false;
}
