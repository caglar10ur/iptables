#ifndef _XT_CLASSIFY_H
#define _XT_CLASSIFY_H

#include <linux/types.h>

struct xt_classify_target_info {
	__u32 priority;
	__u8 add_mark;
};

#endif /*_XT_CLASSIFY_H */
