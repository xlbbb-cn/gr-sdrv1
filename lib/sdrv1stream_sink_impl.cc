/* -*- c++ -*- */
/*
 * Copyright 2025 leonard.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "sdrv1stream_sink_impl.h"
#include <gnuradio/iio/iio_types.h>
#include <gnuradio/io_signature.h>

namespace gr {
namespace sdrv1 {

#pragma message("set the following appropriately and remove this warning")
using input_type = gr_complex;
sdrv1stream_sink::sptr sdrv1stream_sink::make(const std::string& ip_addr,
                                              const std::string& chn,
                                              int32_t bufsize)
{
    return gnuradio::make_block_sptr<sdrv1stream_sink_impl>(ip_addr, chn, bufsize);
}


/*
 * The private constructor
 */
sdrv1stream_sink_impl::sdrv1stream_sink_impl(const std::string& ip_addr,
                                             const std::string& chn,
                                             int32_t bufsize)
    : gr::sync_block("sdrv1stream_sink",
                     gr::io_signature::make(
                         1 /* min inputs */, 1 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(0, 0, 0))
{
    unsigned int chs;
    uint32_t val;
    iio_channel* ch;

    buffer_size = bufsize;

    set_output_multiple(buffer_size);
    ctx = iio_create_network_context(ip_addr.c_str());
    if (!ctx)
        throw std::runtime_error("Unable to create context");

    dev = iio_context_find_device(ctx, "avc_txstream");
    dev_reg = iio_context_find_device(ctx, "avc_rxstream");
    phy = iio_context_find_device(ctx, "rfic-phy");
    if (!dev || !phy || !dev_reg) {
        iio_context_destroy(ctx);
        throw std::runtime_error("Device not found");
    }

    // enable channels
    chs = iio_device_get_channels_count(dev);
    for (unsigned int i = 0; i < chs; i++)
        iio_channel_disable(iio_device_get_channel(dev, i));


    iio_device_reg_read(dev_reg, 0x0, &val);

    val &= ~0x3;

    if (!strcmp("tx1", chn.c_str())) {
        iio_device_reg_write(dev_reg, 0x0, val | 0x1);
        ch = iio_device_find_channel(dev, "voltage0", true);
        iio_channel_enable(ch);
        ch = iio_device_find_channel(dev, "voltage1", true);
        iio_channel_enable(ch);

    } else if (!strcmp("tx2", chn.c_str())) {
        iio_device_reg_write(dev_reg, 0x0, val | 0x2);
        ch = iio_device_find_channel(dev, "voltage2", true);
        iio_channel_enable(ch);
        ch = iio_device_find_channel(dev, "voltage3", true);
        iio_channel_enable(ch);
    } else {
        throw std::runtime_error("chn error:" + chn);
    }


    buf = iio_device_create_buffer(dev, buffer_size, false);
    if (!buf)
        throw std::runtime_error("Unable to create buffer: " + std::to_string(-errno));

    iio_buffer_set_blocking_mode(buf, true);
}

/*
 * Our virtual destructor.
 */
sdrv1stream_sink_impl::~sdrv1stream_sink_impl() {}

uint16_t convert(float d) { return (uint16_t)(d * 32767.0); }

int sdrv1stream_sink_impl::work(int noutput_items,
                                gr_vector_const_void_star& input_items,
                                gr_vector_void_star& output_items)
{
    int ret = 0;
    auto in = static_cast<const input_type*>(input_items[0]);
    double max = 0.0;

    if (noutput_items < buffer_size) {
        throw std::runtime_error("Invalid packet size, expected min " +
                                 std::to_string(buffer_size) + " and got " +
                                 std::to_string(noutput_items) + "!");
    }


    uint32_t* sample_32 = (uint32_t*)new char[buffer_size * sizeof(uint32_t)];
    for (int i = 0; i < buffer_size; ++i) {
        sample_32[i] = ((uint32_t)convert(std::real(in[i])) << 16) |
                       ((uint32_t)convert(std::imag(in[i])) << 0);
    }


    memcpy(iio_buffer_start(buf),
           (void*)sample_32,
           static_cast<char*>(iio_buffer_end(buf)) -
           static_cast<char*>(iio_buffer_start(buf)));

    delete sample_32;

    ret = iio_buffer_push(buf);
    if (ret < 0) {
        char buf[256];
        iio_strerror(-ret, buf, sizeof(buf));
        std::string error(buf);

        d_logger->warn("Unable to push buffer: {:s}", error);
        return WORK_DONE; /* EOF */
    }

    // Tell runtime system how many input items we consumed on
    // each input stream.
    // consume_each(buffer_size);


    // Tell runtime system how many output items we produced.
    return buffer_size;
}

} /* namespace sdrv1 */
} /* namespace gr */
