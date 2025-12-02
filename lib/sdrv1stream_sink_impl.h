/* -*- c++ -*- */
/*
 * Copyright 2025 leonard.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SDRV1_SDRV1STREAM_SINK_IMPL_H
#define INCLUDED_SDRV1_SDRV1STREAM_SINK_IMPL_H

#include <gnuradio/sdrv1/sdrv1stream_sink.h>
#include <iio.h>

namespace gr {
namespace sdrv1 {

class sdrv1stream_sink_impl : public sdrv1stream_sink
{
private:
    iio_context* ctx;
    iio_device *dev, *phy,*dev_reg;
    iio_buffer* buf;


    int32_t buffer_size;

public:
    sdrv1stream_sink_impl(const std::string& ip_addr,
                          const std::string& chn,
                          int32_t bufsize);
    ~sdrv1stream_sink_impl();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sdrv1
} // namespace gr

#endif /* INCLUDED_SDRV1_SDRV1STREAM_SINK_IMPL_H */
